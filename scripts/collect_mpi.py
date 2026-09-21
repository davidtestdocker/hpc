"""Collect JobSet completion and rank evidence; does not submit or modify jobs."""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from scripts.platform import CONTEXT, NAMESPACE, command


def ranks_from_log(log):
    # SSH warning 不算 rank；用固定格式擷取並排序，避免依賴 log 輸出順序。
    return sorted({int(rank) for rank in re.findall(r"^RANK=(\d+) HOST=\S+", log, re.MULTILINE)})


def collect(context, name, output, timeout):
    # 只觀察指定 JobSet，直到 Completed、Failed 或超過觀察期限，不改動工作。
    base = ["kubectl", "--context", context, "--request-timeout=15s", "-n", NAMESPACE]
    deadline = time.monotonic() + timeout
    while True:
        # JobSet condition 是完成判斷的來源，不以 Pod Running 代替工作成功。
        jobset = json.loads(command(base + ["get", "jobset", name, "-o", "json"]))
        conditions = jobset.get("status", {}).get("conditions", [])
        completed = any(c["type"] == "Completed" and c["status"] == "True" for c in conditions)
        failed = any(c["type"] == "Failed" and c["status"] == "True" for c in conditions)
        if completed or failed or time.monotonic() >= deadline:
            break
        print(f"waiting for {name} completion", flush=True)
        time.sleep(5)
    pods = json.loads(command(base + ["get", "pods", "-l", f"jobset.sigs.k8s.io/jobset-name={name}", "-o", "json"]))
    # launcher log 是 rank evidence；Pod 尚未可讀時保留錯誤而不偽造成功結果。
    try:
        log = command(base + ["logs", f"job/{name}-launcher-0", "-c", "launcher", "--pod-running-timeout=1s"])
    except RuntimeError as exc:
        log = ""
        log_error = str(exc)
    else:
        log_error = None
    ranks = ranks_from_log(log)
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(), "context": context,
        "jobset": name, "uid": jobset["metadata"]["uid"],
        "scope": "direct JobSet CPU MPI rank smoke test; not API lifecycle or performance benchmark",
        "passed": completed and ranks == [0, 1, 2], "completed": completed, "failed": failed,
        "ranks": ranks, "conditions": conditions, "launcher_log": log, "log_error": log_error,
        "pods": [{"name": p["metadata"]["name"], "node": p["spec"].get("nodeName"),
                  "phase": p.get("status", {}).get("phase")} for p in pods["items"]],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    return report["passed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobset")
    parser.add_argument("--context", default=CONTEXT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=360)
    args = parser.parse_args()
    return 0 if collect(args.context, args.jobset, args.output, args.timeout) else 1


if __name__ == "__main__":
    sys.exit(main())
