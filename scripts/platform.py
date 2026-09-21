"""Render the main platform or inspect prerequisites without mutating a cluster."""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = "hpc-platform-dev"
CONTEXT = "gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg"


def command(args):
    # 統一由 repo 根目錄執行外部工具，並以 timeout 避免認證或 API server 卡住。
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"{args[0]} unavailable or timed out") from exc
    if result.returncode:
        # Avoid putting credential-plugin stderr into saved evidence.
        raise RuntimeError(f"command failed (exit {result.returncode}): {' '.join(args)}")
    return result.stdout


def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])


def ready_nodes(nodes, pool, gpu=False):
    # Ready 還不夠：節點也必須可排程；GPU 檢查另外要求公布 NVIDIA 資源。
    for node in nodes.get("items", []):
        if node["metadata"].get("labels", {}).get("cloud.google.com/gke-nodepool") != pool:
            continue
        if node.get("spec", {}).get("unschedulable", False):
            continue
        status = node.get("status", {})
        ready = any(c["type"] == "Ready" and c["status"] == "True"
                    for c in status.get("conditions", []))
        if ready and (not gpu or int(status.get("allocatable", {}).get("nvidia.com/gpu", 0)) > 0):
            return True
    return False


def inspect(context, require_gpu=True):
    # 這份盤點只讀 Kubernetes metadata，不讀 Secret data，也不執行 workload。
    checks = []
    base = ["kubectl", "--context", context, "--request-timeout=15s"]

    def check(name, args, predicate=lambda data: True):
        # 單項失敗留在報告中，讓操作者一次看到所有前置條件，而不是遇到第一項就退出。
        try:
            data = json.loads(command(base + args + ["-o", "json"]))
            passed = bool(predicate(data))
            detail = "verified" if passed else "resource exists but readiness condition not met"
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            passed, detail = False, str(exc)
        checks.append({"name": name, "passed": passed, "detail": detail})

    check("system node ready", ["get", "nodes"], lambda d: ready_nodes(d, "system-pool"))
    if require_gpu:
        check("GPU resource advertised", ["get", "nodes"],
              lambda d: ready_nodes(d, "gpu-pool", True))
    check("namespace", ["get", "namespace", NAMESPACE])
    for crd in ["jobsets.jobset.x-k8s.io", "localqueues.kueue.x-k8s.io"]:
        check(crd, ["get", "crd", crd], lambda d: any(
            c["type"] == "Established" and c["status"] == "True"
            for c in d.get("status", {}).get("conditions", [])))
    for namespace in ["jobset-system", "kueue-system"]:
        check(namespace + " controllers", ["get", "deployments", "-n", namespace],
              lambda d: bool(d.get("items")) and all(
                  x.get("spec", {}).get("replicas", 1) > 0 and
                  x.get("status", {}).get("availableReplicas", 0) >= x.get("spec", {}).get("replicas", 1)
                  for x in d["items"]))
    check("local queue active", ["get", "localqueue", "gpu-local-queue", "-n", NAMESPACE],
          lambda d: any(c["type"] == "Active" and c["status"] == "True"
                        for c in d.get("status", {}).get("conditions", [])))
    for secret in ["postgres-secret", "mpi-ssh-key"]:
        # Fetch metadata name only; never fetch Secret data for an inventory report.
        try:
            command(base + ["get", "secret", secret, "-n", NAMESPACE, "-o", "name"])
            checks.append({"name": secret + " exists", "passed": True, "detail": "key contents not inspected"})
        except RuntimeError as exc:
            checks.append({"name": secret + " exists", "passed": False, "detail": str(exc)})
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "context": context, "namespace": NAMESPACE,
        "scope": "read-only prerequisites; not a rebuild or workload acceptance test",
        "passed": all(c["passed"] for c in checks), "checks": checks,
    }


def main():
    # check 產生可追溯 JSON；render 輸出給 server dry-run 或人工檢視。
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["render", "check"])
    parser.add_argument("--context", default=CONTEXT)
    parser.add_argument("--allow-cpu-only", action="store_true",
                        help="Skip only the GPU node prerequisite for infrastructure rehearsal")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.context, require_gpu=not args.allow_cpu_only) if args.action == "check" else None
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if report else render()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content)
        else:
            print(content, end="")
        return 1 if report and not report["passed"] else 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
