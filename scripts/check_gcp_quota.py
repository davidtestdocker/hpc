"""在 Terraform 建立 GPU rehearsal 前，同時檢查區域與全域 GPU quota。"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def quota_map(document):
    return {item["metric"]: {"limit": item["limit"], "usage": item["usage"]}
            for item in document.get("quotas", [])}


def evaluate(region, project, gpu_count, spot):
    regional_name = "PREEMPTIBLE_NVIDIA_L4_GPUS" if spot else "NVIDIA_L4_GPUS"
    regional = quota_map(region).get(regional_name)
    global_gpu = quota_map(project).get("GPUS_ALL_REGIONS")
    checks = []
    for name, quota in ((regional_name, regional), ("GPUS_ALL_REGIONS", global_gpu)):
        available = quota["limit"] - quota["usage"] if quota else 0
        checks.append({
            "metric": name,
            "limit": quota["limit"] if quota else None,
            "usage": quota["usage"] if quota else None,
            "required": gpu_count,
            "available": available,
            "passed": available >= gpu_count,
        })
    return checks


def gcloud_json(args):
    # 只保存 quota 數字，不把 project metadata 或認證錯誤寫入 evidence。
    result = subprocess.run(["gcloud", *args, "--format=json"], capture_output=True,
                            text=True, timeout=60, check=False)
    if result.returncode:
        raise RuntimeError(f"gcloud {args[0]} failed (exit {result.returncode})")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--gpu-count", type=int, default=1)
    parser.add_argument("--spot", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.gpu_count < 1:
        parser.error("--gpu-count must be at least 1")
    try:
        region = gcloud_json(["compute", "regions", "describe", args.region,
                              "--project", args.project])
        project = gcloud_json(["compute", "project-info", "describe",
                               "--project", args.project])
        checks = evaluate(region, project, args.gpu_count, args.spot)
        report = {
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "project": args.project,
            "region": args.region,
            "spot": args.spot,
            "passed": all(item["passed"] for item in checks),
            "checks": checks,
        }
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        report = {"passed": False, "error": str(exc) if isinstance(exc, RuntimeError)
                  else type(exc).__name__}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
