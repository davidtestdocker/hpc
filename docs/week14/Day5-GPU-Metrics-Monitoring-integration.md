# Week14 Day5：GPU Metrics 監控整合（DCGM Exporter + Prometheus + Grafana）

## 今日目標

今天將 GKE GPU Node 的 GPU Metrics 正式整合進既有 Observability 平台。

完成後監控資料流：

```text
Tesla P100 GPU
      │
      ▼
NVIDIA Driver
      │
      ▼
nv-hostengine
      │
      │ TCP 5555
      ▼
DCGM Exporter
      │
      │ HTTP :9400/metrics
      ▼
Prometheus
      │
      ▼
Grafana
```

---

## 1. 確認 DCGM Exporter Helm Chart

加入 NVIDIA Helm Repository：

```bash
helm repo add nvidia https://nvidia.github.io/dcgm-exporter/helm-charts
helm repo update
```

確認版本：

```bash
helm search repo nvidia/dcgm-exporter
```

確認結果：

```text
nvidia/dcgm-exporter
CHART VERSION: 4.8.3
APP VERSION: 4.8.3
```

---

## 2. DCGM Exporter Embedded Mode 問題

最初嘗試直接使用 DCGM Exporter：

```text
dcgm-exporter
    │
    ▼
直接存取 NVIDIA Driver / GPU
```

但 Pod 發生：

```text
CrashLoopBackOff
```

Log：

```text
Starting dcgm-exporter
exit status 1
```

因此改採 Remote DCGM HostEngine 架構：

```text
GPU
 │
 ▼
nv-hostengine
 │
 │ 5555
 ▼
DCGM Exporter
```

將 DCGM HostEngine 與 Exporter 拆開。

---

## 3. 部署 NVIDIA DCGM HostEngine

部署：

```bash
kubectl apply -f benchmark/k8s/nvidia-dcgm.yaml
```

確認 Pod：

```bash
kubectl get pods -n hpc-platform-dev -o wide | grep nvidia-dcgm
```

結果：

```text
nvidia-dcgm-flxx9   1/1   Running
```

查看 Log：

```bash
kubectl logs -n hpc-platform-dev nvidia-dcgm-flxx9
```

結果：

```text
Started host engine version 3.3.0 using port number: 5555
```

代表：

```text
nv-hostengine
```

已成功啟動並監聽：

```text
TCP 5555
```

---

## 4. 建立 DCGM HostEngine Service

確認 Service：

```bash
kubectl get svc -n hpc-platform-dev
```

結果：

```text
nvidia-dcgm   ClusterIP   5555/TCP
```

用途：

```text
DCGM Exporter
      │
      │ nvidia-dcgm:5555
      ▼
Kubernetes Service
      │
      ▼
nv-hostengine
```

Service 提供穩定的 Kubernetes DNS 與 ClusterIP，讓 Remote DCGM Exporter 不需要直接使用 HostEngine Pod IP。

---

## 5. 驗證 HostEngine 網路連線

使用測試 Pod：

```bash
nc -vz nvidia-dcgm 5555
```

結果：

```text
Connection to nvidia-dcgm (...) 5555 port [tcp/*] succeeded!
```

代表：

```text
Pod
 │
 ▼
Service nvidia-dcgm:5555
 │
 ▼
nv-hostengine
```

網路連線正常。

---

## 6. 部署 Remote DCGM Exporter

部署 Remote DCGM Exporter 後確認：

```bash
kubectl get pods -n hpc-platform-dev -o wide | grep dcgm
```

結果：

```text
nvidia-dcgm-exporter-pvcq4   1/1   Running
nvidia-dcgm-flxx9            1/1   Running
```

目前架構：

```text
Tesla P100
     │
     ▼
NVIDIA Driver
     │
     ▼
nv-hostengine
     │
     │ :5555
     ▼
nvidia-dcgm Service
     │
     ▼
Remote DCGM Exporter
```

---

## 7. 建立 DCGM Exporter Service

建立：

```text
benchmark/k8s/nvidia-dcgm-exporter-service.yaml
```

內容：

```yaml
apiVersion: v1
kind: Service

metadata:
  name: nvidia-dcgm-exporter
  namespace: hpc-platform-dev

spec:
  selector:
    app: nvidia-dcgm-exporter

  ports:
    # metrics 是這個 Service Port 的名稱
    # Prometheus Kubernetes Service Discovery 可透過 Port Name 過濾 Endpoint
    - name: metrics
      port: 9400
      targetPort: 9400
```

套用：

```bash
kubectl apply -f benchmark/k8s/nvidia-dcgm-exporter-service.yaml
```

確認：

```bash
kubectl get svc -n hpc-platform-dev
```

結果：

```text
nvidia-dcgm-exporter   ClusterIP   9400/TCP
```

---

## 8. 驗證 DCGM Metrics Endpoint

Port Forward：

```bash
kubectl port-forward svc/nvidia-dcgm-exporter \
  -n hpc-platform-dev \
  9400:9400
```

驗證：

```bash
curl http://127.0.0.1:9400/metrics | head -40
```

成功取得：

```text
DCGM_FI_DEV_GPU_UTIL
DCGM_FI_DEV_FB_FREE
DCGM_FI_DEV_FB_USED
DCGM_FI_DEV_FB_TOTAL
DCGM_FI_DEV_GPU_TEMP
DCGM_FI_DEV_POWER_USAGE
```

實際 GPU：

```text
modelName="Tesla P100-PCIE-16GB"
```

範例：

```text
DCGM_FI_DEV_GPU_UTIL = 0
DCGM_FI_DEV_FB_FREE = 16269 MiB
DCGM_FI_DEV_FB_USED = 0 MiB
DCGM_FI_DEV_FB_TOTAL = 16384 MiB
DCGM_FI_DEV_GPU_TEMP = 51 °C
DCGM_FI_DEV_POWER_USAGE = 29.328 W
```

代表：

```text
GPU
 ↓
DCGM
 ↓
DCGM Exporter
 ↓
/metrics
```

已成功。

---

## 9. Prometheus 加入 GPU Scrape Job

修改：

```text
helm/prometheus/templates/configmap.yaml
```

在：

```yaml
scrape_configs:
```

加入：

```yaml
      - job_name: gpu-metrics

        kubernetes_sd_configs:
          - role: endpoints

        relabel_configs:

          # 只保留 DCGM Exporter Service
          - source_labels: [__meta_kubernetes_service_name]
            action: keep
            regex: nvidia-dcgm-exporter

          # 只保留名稱為 metrics 的 Port
          - source_labels: [__meta_kubernetes_endpoint_port_name]
            action: keep
            regex: metrics
```

其中：

```text
__meta_kubernetes_service_name
```

用來辨識：

```text
nvidia-dcgm-exporter
```

而：

```text
__meta_kubernetes_endpoint_port_name
```

用來辨識 Service 中：

```yaml
name: metrics
```

的 Port。

因此 Prometheus 最後會抓：

```text
nvidia-dcgm-exporter:9400
```

---

## 10. GitOps / Argo CD 同步

目前 Dev Environment 由 Argo CD 管理：

```text
Git Repository
      │
      ▼
Argo CD
      │
      ▼
hpc-platform-dev
```

Application：

```text
hpc-dev
```

並啟用：

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

因此 Git 為 Source of Truth。

手動修改 Cluster Resource 可能會被 Argo CD Self Heal 還原。

正確流程：

```text
修改程式碼
    ↓
git commit
    ↓
git push
    ↓
Argo CD Auto Sync
    ↓
GKE
```

同步後確認：

```bash
kubectl get application hpc-dev -n argocd -w
```

結果：

```text
hpc-dev   Synced   Healthy
```

---

## 11. 驗證 Prometheus GPU Metrics

Port Forward：

```bash
kubectl port-forward svc/prometheus \
  -n hpc-platform-dev \
  9090:9090
```

查詢：

```bash
curl 'http://127.0.0.1:9090/api/v1/query?query=DCGM_FI_DEV_GPU_TEMP'
```

成功取得：

```text
job="gpu-metrics"
modelName="Tesla P100-PCIE-16GB"
device="nvidia0"
gpu="0"
value="51"
```

代表：

```text
DCGM Exporter
      │
      ▼
Service :9400
      │
      ▼
Prometheus
```

已成功串接。

---

## 12. Grafana 驗證

Port Forward：

```bash
kubectl port-forward svc/grafana \
  -n hpc-platform-dev \
  3000:80
```

進入 Grafana：

```text
Explore
→ Prometheus
```

執行 PromQL：

```promql
DCGM_FI_DEV_GPU_TEMP
```

Grafana 成功取得：

```text
51 °C
```

並可看到：

```text
job="gpu-metrics"
device="nvidia0"
gpu="0"
modelName="Tesla P100-PCIE-16GB"
```

代表 Grafana 已成功讀取 Prometheus 中的 GPU Metrics。

---

## 13. 目前 GPU Metrics

| Metric | 用途 | 單位 |
|---|---|---|
| `DCGM_FI_DEV_GPU_UTIL` | GPU 使用率 | % |
| `DCGM_FI_DEV_GPU_TEMP` | GPU 溫度 | °C |
| `DCGM_FI_DEV_POWER_USAGE` | GPU 功耗 | W |
| `DCGM_FI_DEV_FB_USED` | 已使用 VRAM | MiB |
| `DCGM_FI_DEV_FB_FREE` | 剩餘 VRAM | MiB |
| `DCGM_FI_DEV_FB_TOTAL` | VRAM 總容量 | MiB |

---

## 14. Day5 最終架構

```text
GKE GPU Node
gke-hpc-dev-gpu-pool
        │
        ▼
Tesla P100-PCIE-16GB
        │
        ▼
NVIDIA Driver
        │
        ▼
nv-hostengine
        │
        │ TCP 5555
        ▼
Service: nvidia-dcgm
        │
        ▼
Remote DCGM Exporter
        │
        │ HTTP :9400/metrics
        ▼
Service: nvidia-dcgm-exporter
        │
        ▼
Prometheus
job="gpu-metrics"
        │
        ▼
Grafana Explore
```

---

## Day5 完成結果

完成 GPU Monitoring Pipeline：

```text
GPU
→ NVIDIA Driver
→ DCGM HostEngine
→ DCGM Exporter
→ Prometheus
→ Grafana
```

實際驗證：

```text
GPU Model       : Tesla P100-PCIE-16GB
GPU Temperature : 51 °C
VRAM Total      : 16384 MiB
GPU Power       : 約 29 W
Prometheus Job  : gpu-metrics
Grafana Query   : Success
```

Week14 Day5 完成 GPU Metrics 與既有 Observability Platform 的整合。
