"""Read terminal MPI JobSet state and launcher rank evidence from Kubernetes."""

import ast
import re

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

NAMESPACE = "hpc-platform-dev"


def classify_jobset(jobset: dict) -> str | None:
    """Return the API job state only when JobSet reports a terminal condition."""
    status = jobset.get("status", {})
    terminal_state = str(status.get("terminalState", "")).lower()
    if terminal_state in {"completed", "failed"}:
        return terminal_state

    conditions = status.get("conditions", [])
    for terminal_type, api_status in (("Completed", "completed"), ("Failed", "failed")):
        if any(
            condition.get("type") == terminal_type
            and condition.get("status") == "True"
            for condition in conditions
        ):
            return api_status
    return None


def ranks_from_log(log: str) -> list[int]:
    """Extract unique MPI ranks without depending on interleaved log order."""
    return sorted(
        {int(rank) for rank in re.findall(r"^RANK=(\d+) HOST=\S+", log, re.MULTILINE)}
    )


def normalize_log(log: str | bytes) -> str:
    """Normalize Kubernetes client responses before parsing or JSON serialization."""
    if isinstance(log, bytes):
        return log.decode("utf-8", errors="replace")
    # Some Kubernetes client/runtime combinations return the repr of bytes as a string.
    if log.startswith(("b'", 'b"')):
        try:
            decoded = ast.literal_eval(log)
        except (SyntaxError, ValueError):
            return log
        if isinstance(decoded, bytes):
            return decoded.decode("utf-8", errors="replace")
    return log


def build_terminal_update(
    jobset_name: str,
    jobset: dict,
    launcher_log: str,
    log_error: str | None = None,
) -> dict | None:
    """Build the Redis/API update while preserving JobSet as success authority."""
    state = classify_jobset(jobset)
    if state is None:
        return None

    ranks = ranks_from_log(launcher_log)
    conditions = jobset.get("status", {}).get("conditions", [])
    message = "MPI JobSet completed" if state == "completed" else "MPI JobSet failed"
    return {
        "status": state,
        "result": {
            "message": message,
            "jobset_name": jobset_name,
            "ranks": ranks,
            "rank_evidence_complete": ranks == [0, 1, 2],
            "launcher_log": launcher_log,
            "log_error": log_error,
            "conditions": conditions,
        },
    }


def collect_mpi_jobset(jobset_name: str, namespace: str = NAMESPACE) -> dict | None:
    """Query one JobSet and return an update only after it reaches a terminal state."""
    # API Pod 使用 ServiceAccount；本機只讀驗收可沿用明確設定的 kubeconfig context。
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    custom_api = client.CustomObjectsApi()
    core_api = client.CoreV1Api()

    jobset = custom_api.get_namespaced_custom_object(
        group="jobset.x-k8s.io",
        version="v1alpha2",
        namespace=namespace,
        plural="jobsets",
        name=jobset_name,
    )
    if classify_jobset(jobset) is None:
        return None

    # Labels survive generated Pod suffixes and JobSet restarts, unlike a guessed Pod name.
    selector = (
        f"jobset.sigs.k8s.io/jobset-name={jobset_name},"
        "jobset.sigs.k8s.io/replicatedjob-name=launcher"
    )
    launcher_pods = core_api.list_namespaced_pod(
        namespace=namespace,
        label_selector=selector,
    ).items

    if not launcher_pods:
        launcher_log = ""
        log_error = "launcher pod not found"
    else:
        launcher_pod = max(
            launcher_pods,
            key=lambda pod: pod.metadata.creation_timestamp,
        )
        try:
            launcher_log = normalize_log(
                core_api.read_namespaced_pod_log(
                    name=launcher_pod.metadata.name,
                    namespace=namespace,
                    container="launcher",
                )
            )
        except ApiException as exc:
            launcher_log = ""
            log_error = f"{type(exc).__name__}: {exc}"
        else:
            log_error = None

    return build_terminal_update(jobset_name, jobset, launcher_log, log_error)
