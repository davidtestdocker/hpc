import yaml
from kubernetes import client, config

from api.workloads.renderer import render_mpi_jobset


NAMESPACE = "hpc-platform-dev"


def submit_mpi_jobset(job_id: str) -> str:
    config.load_incluster_config()

    manifest_yaml = render_mpi_jobset(job_id)
    manifest = yaml.safe_load(manifest_yaml)

    api = client.CustomObjectsApi()

    response = api.create_namespaced_custom_object(
        group="jobset.x-k8s.io",
        version="v1alpha2",
        namespace=NAMESPACE,
        plural="jobsets",
        body=manifest,
    )

    return response["metadata"]["name"]
