"""以釘版 controllers、排程資源與 runtime Secrets bootstrap 新 GKE 叢集。"""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from scripts.deploy_platform import deploy
from scripts.platform import NAMESPACE, ROOT, ready_nodes

CONTROLLERS = {
    "jobset": {
        "version": "v0.12.0",
        "url": "https://github.com/kubernetes-sigs/jobset/releases/download/v0.12.0/manifests.yaml",
        "sha256": "a41aaf12dd0b7b0a3d626b8d6107f32c3dc889d7e7830adc46b8cdb77a8963bb",
        "deployment": "jobset-system/jobset-controller-manager",
    },
    "kueue": {
        "version": "v0.19.2",
        "url": "https://github.com/kubernetes-sigs/kueue/releases/download/v0.19.2/manifests.yaml",
        "sha256": "88881eb50734eb920b67486ebc2aa978ed325e1b12d99b22fc51a6d7e9e4d370",
        "deployment": "kueue-system/kueue-controller-manager",
    },
}

SCHEDULING = [
    "k8s/gpu-scheduling/topology.yaml",
    "k8s/gpu-scheduling/resourceflavor.yaml",
    "k8s/gpu-scheduling/clusterqueue.yaml",
    "k8s/gpu-scheduling/localqueue.yaml",
    "k8s/gpu-scheduling/priorityclasses.yaml",
]


def download_controller(name, target):
    # Release URL 與 digest 同時鎖定，避免相同操作取得不同或遭竄改的 manifest。
    metadata = CONTROLLERS[name]
    with urllib.request.urlopen(metadata["url"], timeout=60) as response:
        content = response.read()
    digest = hashlib.sha256(content).hexdigest()
    if digest != metadata["sha256"]:
        raise RuntimeError(f"{name} manifest checksum mismatch")
    target.write_bytes(content)


def validate_postgres_env(path):
    # 僅回傳鍵名集合；錯誤與 evidence 都不包含密碼值。
    values = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError("PostgreSQL env file 格式錯誤")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    required = {"POSTGRES_USER", "POSTGRES_PASSWORD"}
    if any(not values.get(key) for key in required):
        raise RuntimeError("PostgreSQL env file 缺少必要且非空的鍵")
    if any(values[key] == "CHANGE_ME" for key in required):
        raise RuntimeError("PostgreSQL env file 仍含 CHANGE_ME")
    return set(values)


def bootstrap(context, execute, output, postgres_env_file=None, require_gpu=True):
    report = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "context": context,
        "execute": execute,
        "passed": False,
        "controller_versions": {name: data["version"] for name, data in CONTROLLERS.items()},
        "steps": [],
    }
    base = ["kubectl", "--context", context, "--request-timeout=30s"]

    def run(args, *, input_text=None, timeout=180):
        result = subprocess.run(base + args, cwd=ROOT, input=input_text, capture_output=True,
                                text=True, timeout=timeout, check=False)
        if result.returncode:
            # 不將可能包含 Secret YAML 的 stdout/stderr寫入 evidence。
            raise RuntimeError(f"kubectl {args[0]} failed (exit {result.returncode})")
        return result.stdout

    def record(message):
        report["steps"].append(message)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(message, flush=True)

    def exists(kind, name, namespace=None):
        args = ["get", kind, name]
        if namespace:
            args += ["-n", namespace]
        result = subprocess.run(base + args + ["-o", "name"], cwd=ROOT,
                                capture_output=True, text=True, timeout=30, check=False)
        return result.returncode == 0

    def apply_secret(args):
        secret = subprocess.run(base + ["create", "secret", "generic"] + args
                                + ["--dry-run=client", "-o", "yaml"], cwd=ROOT,
                                capture_output=True, text=True, timeout=30, check=False)
        if secret.returncode:
            raise RuntimeError("kubectl create secret failed")
        run(["apply", "-f", "-"], input_text=secret.stdout)

    try:
        nodes = json.loads(run(["get", "nodes", "-o", "json"]))
        if not ready_nodes(nodes, "system-pool"):
            raise RuntimeError("system-pool 沒有 Ready 且可排程的 node")
        if require_gpu and not ready_nodes(nodes, "gpu-pool", gpu=True):
            raise RuntimeError("gpu-pool 沒有 Ready 且已公布 GPU 的 node")
        record("system and GPU node prerequisites passed" if require_gpu
               else "system node prerequisite passed; CPU-only rehearsal selected")

        with tempfile.TemporaryDirectory(prefix="hpc-bootstrap-") as directory:
            manifests = {}
            for name in CONTROLLERS:
                path = Path(directory) / f"{name}.yaml"
                download_controller(name, path)
                manifests[name] = path
            record("pinned controller manifests downloaded and verified")

            if execute:
                for name, path in manifests.items():
                    run(["apply", "--server-side", "-f", str(path)], timeout=300)
                    deployment = CONTROLLERS[name]["deployment"]
                    namespace, resource = deployment.split("/", 1)
                    # 先套 placement／request 再等待，避免小型 system node 上的原始 request 卡住。
                    patch = ("k8s/controllers/jobset-demo-resources-patch.yaml" if name == "jobset"
                             else "k8s/controllers/kueue-system-pool-patch.yaml")
                    run(["patch", "deployment", resource, "-n", namespace,
                         "--type=strategic", "--patch-file", patch])
                    run(["rollout", "status", f"deployment/{resource}", "-n", namespace,
                         "--timeout=240s"], timeout=270)
                    record(f"{name} controller installed and ready")

                run(["apply", "-f", "k8s/bootstrap/namespace.yaml"])
                record("namespace and controller system-pool placement applied")

                for manifest in SCHEDULING:
                    run(["apply", "-f", manifest])
                record("Kueue topology, flavor, queues and priorities applied")

                if not exists("secret", "postgres-secret", NAMESPACE):
                    if not postgres_env_file:
                        raise RuntimeError("新環境需要 --postgres-env-file 建立 postgres-secret")
                    validate_postgres_env(postgres_env_file)
                    apply_secret(["postgres-secret", "-n", NAMESPACE,
                                  "--from-env-file", str(postgres_env_file)])
                    record("postgres-secret created from external env file")
                else:
                    record("existing postgres-secret retained")

                if not exists("secret", "mpi-ssh-key", NAMESPACE):
                    with tempfile.TemporaryDirectory(prefix="mpi-key-") as key_directory:
                        key_path = Path(key_directory)
                        for algorithm, filename, extra in (("ed25519", "id_ed25519", []),
                                                           ("rsa", "id_rsa", ["-b", "3072"])):
                            subprocess.run(["ssh-keygen", "-q", "-t", algorithm, *extra, "-N", "",
                                            "-f", str(key_path / filename)], check=True, timeout=30)
                        authorized = ((key_path / "id_ed25519.pub").read_text()
                                      + (key_path / "id_rsa.pub").read_text())
                        (key_path / "authorized_keys").write_text(authorized)
                        apply_secret(["mpi-ssh-key", "-n", NAMESPACE,
                                      "--from-file=id_ed25519=" + str(key_path / "id_ed25519"),
                                      "--from-file=id_rsa=" + str(key_path / "id_rsa"),
                                      "--from-file=authorized_keys=" + str(key_path / "authorized_keys")])
                    record("ephemeral MPI keys generated; Kubernetes Secret created")
                else:
                    record("existing mpi-ssh-key retained")

                platform_report = output.with_name(output.stem + "-platform.json")
                if deploy(context, True, platform_report, require_gpu=require_gpu):
                    raise RuntimeError("platform overlay deployment failed")
                report["platform_report"] = platform_report.name
                record("platform overlay deployed")
            else:
                # 現有環境驗證所有宣告資源是否仍可由 API server 接受，不做 mutation。
                for manifest in SCHEDULING:
                    run(["apply", "--dry-run=server", "-f", manifest])
                record("scheduling manifests server dry-run passed")
                platform_report = output.with_name(output.stem + "-platform.json")
                if deploy(context, False, platform_report, require_gpu=require_gpu):
                    raise RuntimeError("platform overlay server dry-run failed")
                report["platform_report"] = platform_report.name
                record("platform overlay server dry-run passed; no resources changed")

        report["passed"] = True
        record("bootstrap passed" if execute else "bootstrap validation passed")
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        report["error"] = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        record("failed; completed resources were retained for inspection")
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--postgres-env-file", type=Path)
    parser.add_argument("--allow-cpu-only", action="store_true",
                        help="Validate infrastructure without a GPU node or MPI acceptance")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    return bootstrap(args.context, args.execute, args.output, args.postgres_env_file,
                     require_gpu=not args.allow_cpu_only)


if __name__ == "__main__":
    sys.exit(main())
