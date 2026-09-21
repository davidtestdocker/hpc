"""Re-admit a Pending JobSet whose Pods select a node that no longer exists."""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.platform import CONTEXT, NAMESPACE, command


def stale_pending_pods(pods, node_names):
    # 只允許全部仍 Pending 且 selector 指向不存在 node 的狀態，避免驅逐 Running 工作。
    if not pods or any(p.get("status", {}).get("phase") != "Pending" for p in pods):
        raise RuntimeError("Recovery only supports a JobSet with exclusively Pending Pods")
    stale = [p["metadata"]["name"] for p in pods
             if (host := p.get("spec", {}).get("nodeSelector", {}).get("kubernetes.io/hostname"))
             and host not in node_names]
    if not stale:
        raise RuntimeError("No missing hostname selector found; diagnose the actual scheduling failure")
    return stale


def recover(context, workload_name, output, execute=False):
    # 先驗證 Workload 與 JobSet owner UID，避免名稱重用造成誤操作。
    base = ["kubectl", "--context", context, "--request-timeout=15s", "-n", NAMESPACE]

    def get(*args):
        return json.loads(command(base + ["get", *args, "-o", "json"]))

    workload = get("workload", workload_name)
    owners = [o for o in workload["metadata"].get("ownerReferences", []) if o["kind"] == "JobSet"]
    if len(owners) != 1 or not workload["spec"].get("active", True):
        raise RuntimeError("Expected an active Workload owned by one JobSet")
    owner = owners[0]
    jobset = get("jobset", owner["name"])
    if jobset["metadata"]["uid"] != owner["uid"]:
        raise RuntimeError("JobSet owner UID mismatch")
    selector = "jobset.sigs.k8s.io/jobset-name=" + owner["name"]
    pods = get("pods", "-l", selector)["items"]
    nodes = get("nodes")["items"]
    hosts = {n["metadata"].get("labels", {}).get("kubernetes.io/hostname") for n in nodes}
    stale = stale_pending_pods(pods, hosts)
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(), "context": context,
        "workload": workload_name, "jobset": owner["name"], "stale_pods": stale,
        "old_hostnames": [p["spec"].get("nodeSelector", {}).get("kubernetes.io/hostname") for p in pods],
        "executed": execute, "reactivated": False, "placement_recovered": False,
    }

    def save():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n")

    def active(value):
        # JSON patch 的 test 保護 resource identity；active=false 會讓 Kueue 撤銷准入。
        patch = [{"op": "test", "path": "/metadata/uid", "value": workload["metadata"]["uid"]},
                 {"op": "add", "path": "/spec/active", "value": value}]
        command(base + ["patch", "workload", workload_name, "--type=json", "-p", json.dumps(patch)])

    save()
    if not execute:
        return report
    # Recheck immediately before eviction; never intentionally stop Running Pods.
    stale_pending_pods(get("pods", "-l", selector)["items"], hosts)
    try:
        # 重新檢查後才停用；若撤銷准入沒有在期限內完成，保留錯誤並恢復 active。
        active(False)
        print("Workload deactivated; waiting for old admission to clear", flush=True)
        for _ in range(30):
            current = get("workload", workload_name)
            if not current.get("status", {}).get("admission") and not get("pods", "-l", selector)["items"]:
                break
            time.sleep(2)
        else:
            raise RuntimeError("Old admission or Pods did not clear")
    except RuntimeError as exc:
        report["error"] = str(exc)
        save()
        raise
    finally:
        # Resume eligibility even if admission clearing fails; preserve workload identity.
        active(True)
        report["reactivated"] = True
        save()
    for _ in range(60):
        current_pods = get("pods", "-l", selector)["items"]
        report["pods_after"] = [{"name": p["metadata"]["name"], "node": p["spec"].get("nodeName"),
                                 "phase": p.get("status", {}).get("phase")} for p in current_pods]
        expected = len(pods)
        if len(current_pods) == expected and all(
                p["spec"].get("nodeName") and p.get("status", {}).get("phase") in {"Running", "Succeeded"}
                for p in current_pods):
            report["placement_recovered"] = True
            save()
            return report
        print("waiting for new admission and Pod placement", flush=True)
        time.sleep(5)
    report["error"] = "Workload reactivated but placement did not recover in the observation window"
    save()
    raise RuntimeError("Workload reactivated but placement did not recover in the observation window")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workload")
    parser.add_argument("--context", default=CONTEXT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    try:
        report = recover(args.context, args.workload, args.output, args.execute)
        print(json.dumps(report, indent=2))
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
