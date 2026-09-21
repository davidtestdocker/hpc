# 使用 Pod 的叢集內身分呼叫 Kubernetes API，建立指定 namespace 的 MPI JobSet。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import yaml
from kubernetes import client, config

from api.workloads.renderer import render_mpi_jobset


NAMESPACE = "hpc-platform-dev"


# 載入叢集內認證，解析 YAML 並建立 JobSet 自訂資源。
def submit_mpi_jobset(job_id: str) -> str:
    # 讀取 Pod 掛載的 ServiceAccount token 與叢集 API 設定。
    config.load_incluster_config()

    manifest_yaml = render_mpi_jobset(job_id)
    # 將 YAML 解析為 Python 資料，不建立任意 Python 物件。
    manifest = yaml.safe_load(manifest_yaml)

    api = client.CustomObjectsApi()

    # 依 group／version／plural 呼叫自訂資源 API；body 是完整 manifest。
    response = api.create_namespaced_custom_object(
        group="jobset.x-k8s.io",
        version="v1alpha2",
        namespace=NAMESPACE,
        plural="jobsets",
        body=manifest,
    )

    return response["metadata"]["name"]
