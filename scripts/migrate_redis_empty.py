"""Move an EMPTY demo Redis to a new PVC, then verify persistence after restart.

Requires a maintenance window. Refuses non-empty Redis (including other DBs),
existing PVCs, and an already persistent deployment. Never flushes any data.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import yaml

from scripts.platform import CONTEXT, NAMESPACE, render


def require_empty_keyspace(info):
    # 任一 Redis database 出現 dbN 都代表有資料；遷移工具禁止自行覆蓋或 flush。
    databases = [line for line in info.splitlines() if line.startswith("db")]
    if databases:
        raise RuntimeError("Redis contains data; non-empty migration requires a separate backup/restore procedure")


def redis_manifests(rendered):
    # 只取 Redis Deployment／PVC，避免維護腳本誤套用整個平台 overlay。
    items = [item for item in yaml.safe_load_all(rendered) if item]
    selected = [item for item in items if (item["kind"], item["metadata"]["name"]) in {
        ("Deployment", "redis"), ("PersistentVolumeClaim", "redis-pvc"),
    }]
    if len(selected) != 2:
        raise RuntimeError("Expected exactly the Redis deployment and PVC")
    return {"apiVersion": "v1", "kind": "List", "items": selected}


class Migration:
    def __init__(self, context, output):
        self.base = ["kubectl", "--context", context, "--request-timeout=20s", "-n", NAMESPACE]
        self.output = output
        self.report = {"context": context, "namespace": NAMESPACE, "passed": False, "steps": []}

    def record(self, step, **details):
        # 每一步即時寫入報告，維護中斷時仍能追查已完成的動作。
        self.report["steps"].append({"time": datetime.now(timezone.utc).isoformat(), "step": step, **details})
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(self.report, indent=2) + "\n")
        print(step, flush=True)

    def kubectl(self, *args, data=None):
        # 所有 mutation 都經過同一個 context、namespace 與 timeout 設定。
        result = subprocess.run(self.base + list(args), input=data, capture_output=True,
                                text=True, timeout=60, check=False)
        if result.returncode:
            raise RuntimeError(f"kubectl {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout.strip()

    def get(self, kind, name):
        return json.loads(self.kubectl("get", kind, name, "-o", "json"))

    def redis(self, target, *args):
        return self.kubectl("exec", target, "--", "redis-cli", "--raw", "-e", *args)

    def wait_deployment(self, name):
        # rollout 條件必須同時滿足 updated、ready 與 replicas。
        # Short polling commands retain progress output during provisioning.
        for _ in range(60):
            data = self.get("deployment", name)
            wanted = data["spec"].get("replicas", 1)
            status = data.get("status", {})
            if (status.get("observedGeneration", 0) >= data["metadata"]["generation"]
                    and status.get("updatedReplicas", 0) == wanted
                    and status.get("readyReplicas", 0) == wanted
                    and status.get("replicas", 0) == wanted):
                return
            print(f"waiting for deployment/{name}", flush=True)
            time.sleep(5)
        raise RuntimeError(f"deployment/{name} did not converge within the maintenance window")

    def execute(self, manifest):
        # 先做 live 狀態檢查；任何非空或已持久化情況都直接中止。
        self.kubectl("apply", "--dry-run=server", "-f", "-", data=json.dumps(manifest))
        live = self.get("deployment", "redis")
        if any(v.get("persistentVolumeClaim") for v in live["spec"]["template"]["spec"].get("volumes", [])):
            raise RuntimeError("Redis already has persistent storage; migration is not needed")
        if self.kubectl("get", "pvc", "redis-pvc", "--ignore-not-found", "-o", "name"):
            raise RuntimeError("redis-pvc already exists; inspect it rather than overwriting or reusing it")
        pods = json.loads(self.kubectl("get", "pods", "-l", "app=redis", "-o", "json"))["items"]
        if len(pods) != 1 or pods[0]["status"]["phase"] != "Running":
            raise RuntimeError("Expected one running source Redis Pod")
        source = "pod/" + pods[0]["metadata"]["name"]
        require_empty_keyspace(self.redis(source, "INFO", "keyspace"))
        api_replicas = self.get("deployment", "api")["spec"].get("replicas", 1)
        hpas = json.loads(self.kubectl("get", "hpa", "-o", "json"))["items"]
        if any(hpa["spec"]["scaleTargetRef"].get("name") == "api"
               and hpa["spec"].get("minReplicas", 1) == 0 for hpa in hpas):
            raise RuntimeError("API HPA permits scale-to-zero; establish a separate maintenance procedure")
        self.record("preconditions passed", source_uid=pods[0]["metadata"]["uid"], api_replicas=api_replicas)
        api_stopped = False
        source_paused = False
        try:
            # 先停 API，再暫停 Redis writes，縮小切換期間的狀態競爭窗口。
            self.kubectl("scale", "deployment/api", "--replicas=0")
            api_stopped = True
            self.wait_deployment("api")
            self.record("API stopped; HPA with minReplicas > 0 is inactive at zero replicas")
            self.redis(source, "CLIENT", "PAUSE", "300000", "WRITE")
            source_paused = True
            paused_at = time.monotonic()
            require_empty_keyspace(self.redis(source, "INFO", "keyspace"))
            self.record("writes paused; all databases confirmed empty")
            if time.monotonic() - paused_at > 30:
                raise RuntimeError("Pre-apply guard exceeded its time budget")
            self.kubectl("apply", "-f", "-", data=json.dumps(manifest))
            self.record("Redis deployment and new PVC applied")
            self.wait_deployment("redis")
            if self.redis("deployment/redis", "PING") != "PONG":
                raise RuntimeError("New Redis did not respond")
            self.record("Redis ready", pvc_phase=self.get("pvc", "redis-pvc")["status"]["phase"])
            # 寫入唯一 marker，重啟後讀回即可證明 PVC 真的被新 Pod 使用。
            marker = "persistence-check:" + str(uuid4())
            if self.redis("deployment/redis", "SET", marker, "verified", "EX", "3600", "NX") != "OK":
                raise RuntimeError("Could not create persistence marker")
            self.redis("deployment/redis", "SAVE")
            time.sleep(2)  # Allow default appendfsync=everysec before graceful restart.
            self.kubectl("rollout", "restart", "deployment/redis")
            self.wait_deployment("redis")
            if self.redis("deployment/redis", "GET", marker) != "verified":
                raise RuntimeError("Persistence marker missing after Redis Pod replacement")
            self.redis("deployment/redis", "DEL", marker)
            self.record("marker survived Pod replacement; test marker removed")
            self.kubectl("scale", "deployment/api", f"--replicas={api_replicas}")
            self.wait_deployment("api")
            api_stopped = False
            self.report["passed"] = True
            self.record("API restored; empty-database migration and graceful restart verified")
        except Exception:
            if source_paused:
                try:
                    self.redis(source, "CLIENT", "UNPAUSE")
                    self.record("original source unpaused")
                except (RuntimeError, OSError, subprocess.SubprocessError):
                    self.record("source no longer reachable; pause expires automatically")
            if api_stopped:
                # Resume only when there is a reachable Redis; never delete PVC or undo data changes.
                try:
                    if self.redis("deployment/redis", "PING") == "PONG":
                        self.kubectl("scale", "deployment/api", f"--replicas={api_replicas}")
                        self.wait_deployment("api")
                        self.record("API restored after interrupted migration")
                    else:
                        self.record("API remains stopped; Redis recovery required")
                except (RuntimeError, OSError, subprocess.SubprocessError):
                    self.record("API recovery not confirmed; manual inspection required")
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", default=CONTEXT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Stop API briefly and migrate an empty Redis")
    args = parser.parse_args()
    manifest = redis_manifests(render())
    if not args.execute:
        print(json.dumps(manifest, indent=2))
        return 0
    migration = Migration(args.context, args.output)
    try:
        migration.execute(manifest)
        return 0
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        migration.record("migration failed", error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
