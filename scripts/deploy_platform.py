"""檢查或部署平台 overlay；叢集、controllers、queues 與 Secrets 必須先備妥。"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from scripts.platform import NAMESPACE, ROOT, inspect, render


def validate_redis(existing):
    # 只允許新建，或沿用已掛載的同名 PVC；資料遷移交給獨立流程。
    if not existing:
        return
    pod = existing["spec"]["template"]["spec"]
    volumes = {v["name"]: v for v in pod.get("volumes", [])}
    for container in pod.get("containers", []):
        if container["name"] != "redis":
            continue
        for mount in container.get("volumeMounts", []):
            volume = volumes.get(mount["name"], {})
            if (mount.get("mountPath") == "/data"
                    and not mount.get("subPath") and not mount.get("subPathExpr")
                    and volume.get("persistentVolumeClaim", {}).get("claimName") == "redis-pvc"):
                return
    raise RuntimeError("Redis 尚未直接掛載 redis-pvc 至 /data；請先完成資料遷移")


def deploy(context, execute, output, require_gpu=True):
    # 每次都使用顯式 context；報告不保存 Secret、環境變數或 kubectl stderr。
    report = {"context": context, "execute": execute, "passed": False, "steps": []}
    base = ["kubectl", "--context", context, "--request-timeout=30s", "-n", NAMESPACE]

    def run(args, timeout=60):
        result = subprocess.run(base + args, cwd=ROOT, capture_output=True,
                                text=True, timeout=timeout, check=False)
        if result.returncode:
            raise RuntimeError(f"kubectl {args[0]} failed (exit {result.returncode})")
        return result.stdout

    def record(step):
        report["steps"].append(step)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(step, flush=True)

    try:
        report["preflight"] = inspect(context, require_gpu=require_gpu)
        if not report["preflight"]["passed"]:
            raise RuntimeError("前置檢查失敗，詳見 report.preflight")
        record("prerequisites passed")
        existing = run(["get", "deployment", "redis", "--ignore-not-found", "-o", "json"])
        validate_redis(json.loads(existing) if existing.strip() else None)
        record("Redis storage guard passed")

        manifest = render()
        # 此入口只部署不含 Secret 的固定 overlay，避免將密碼寫入暫存或報告。
        if any(doc and doc.get("kind") == "Secret" for doc in yaml.safe_load_all(manifest)):
            raise RuntimeError("Overlay 包含 Secret，請改用外部 Secret provisioning")
        with tempfile.TemporaryDirectory(prefix="hpc-platform-") as directory:
            path = Path(directory) / "platform.yaml"
            path.write_text(manifest)
            run(["apply", "--dry-run=server", "-f", str(path)])
            record("server dry-run passed")
            if execute:
                run(["apply", "-f", str(path)])
                record("overlay applied")
                workloads = ['deployment/redis', 'statefulset/postgres', 'deployment/api']
                if any(doc and doc.get('kind') == 'Deployment'
                       and doc.get('metadata', {}).get('name') == 'api-worker'
                       for doc in yaml.safe_load_all(manifest)):
                    workloads.append('deployment/api-worker')
                for resource in workloads:
                    run(["rollout", "status", resource, "--timeout=180s"], timeout=210)
                    record(f"{resource} rollout passed")
                run(["exec", "deployment/api", "--", "python", "-m", "api.database.init_db"])
                record("database create_all passed (not schema migration)")
        report["passed"] = True
        record("deployment passed" if execute else "dry-run passed; no resources changed")
        return 0
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        # 失敗時保留已套用資源和 PVC，不嘗試回滾資料；report 指出最後成功階段。
        report["error"] = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        record("failed; inspect completed steps before retrying")
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--allow-cpu-only", action="store_true",
                        help="Skip GPU readiness only for infrastructure rehearsal")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    return deploy(args.context, args.execute, args.output,
                  require_gpu=not args.allow_cpu_only)


if __name__ == "__main__":
    sys.exit(main())
