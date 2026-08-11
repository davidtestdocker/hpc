# Week14 Day4 - GKE GPU Node Pool & GPU Scheduling

## 今天平台增加了什麼？

今天平台正式具備 **GPU Workload 執行能力**。

新增能力：

- 建立 GKE GPU Node Pool
- Kubernetes GPU Scheduling
- 第一個 GPU Pod
- 驗證 NVIDIA Driver
- 驗證 CUDA Runtime
- 使用 `nvidia-smi` 監控 GPU
- 了解 GPU Quota 與 GPU Stock 差異
- 完成 GPU Node Troubleshooting

---

# 今天平台架構

```text
                    GKE Cluster (hpc-dev)
                            │
        ┌───────────────────┴────────────────────┐
        │                                        │
 Primary Pool                          Observability Pool
(API / Redis / DB)                (Prometheus / Grafana)
        │
        │
        └────────────────────────────┐
                                     │
                              GPU Pool (P100)
                                     │
                          gpu-test Pod
                                     │
                       nvidia/cuda Image
                                     │
                            nvidia-smi
```

---

# GPU Quota

GPU Quota

代表：

> Project 最多可以使用多少張 GPU。

例如：

```
Quota

NVIDIA_P100_GPUS = 1
```

代表：

目前 Project 最多可以建立一張 P100 GPU。

---

# GPU Stock

GPU Quota 不代表一定建立成功。

GPU 建立需要：

```
GPU Quota
        +
GPU Stock
```

若 Google Cloud 當下沒有 GPU：

```
GCE_STOCKOUT
```

即使：

```
Quota = 1
```

仍會建立失敗。

---

# 本次 Troubleshooting

今天實際遇到：

```
GCE_STOCKOUT
```

排查流程：

- 檢查 GPU Quota
- 檢查 Machine Type
- 檢查 Accelerator Type
- 檢查 Zone
- 建立 Compute Engine GPU VM 驗證

結果：

L4：

```
Stockout
```

P100：

```
Success
```

因此確認：

不是 Kubernetes 問題。

Root Cause：

```
Google Cloud GPU Stock 不足
```

---

# 建立 GPU Node Pool

建立 GPU Node：

```bash
gcloud container node-pools create gpu-pool \
  --cluster=hpc-dev \
  --zone=asia-east1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-p100,count=1,gpu-driver-version=default \
  --num-nodes=1
```

---

# 驗證 GPU Resource

確認 Kubernetes 已辨識 GPU：

```bash
kubectl describe node <gpu-node>
```

成功看到：

```
Capacity:

nvidia.com/gpu: 1

Allocatable:

nvidia.com/gpu: 1
```

代表：

GPU 已成功註冊至 Kubernetes。

---

# GPU Scheduling

Pod 宣告：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Scheduler：

```
Pod
      │
      ▼
讀取 Resource

CPU

Memory

GPU

      │
      ▼

GPU Node
```

Image 不影響 Scheduler。

真正影響 Scheduler：

```
resources.limits
```

---

# GPU Node Taint

GPU Node 自動具有：

```
nvidia.com/gpu=present:NoSchedule
```

用途：

避免一般 CPU Workload 被排到昂貴 GPU Node。

---

# GPU Test Pod

建立：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: gpu-test
  namespace: hpc-platform-dev

spec:
  restartPolicy: Never

  containers:
    - name: gpu-test

      image: nvidia/cuda:12.4.1-base-ubuntu22.04

      command:
        - tail
        - -f
        - /dev/null

      resources:
        limits:
          nvidia.com/gpu: 1
```

部署：

```bash
kubectl apply -f benchmark/k8s/gpu-test-pod.yaml
```

確認：

```bash
kubectl get pod -o wide
```

成功排程：

```
gpu-pool
```

---

# CUDA Image

使用：

```
nvidia/cuda:12.4.1-base-ubuntu22.04
```

內容包含：

- Ubuntu 22.04
- CUDA Runtime 12.4.1

適合作為 GPU Workload Base Image。

---

# 驗證 GPU

進入 Pod：

```bash
kubectl exec -it gpu-test -n hpc-platform-dev -- bash
```

執行：

```bash
nvidia-smi
```

成功：

```
Tesla P100-PCIE-16GB
```

代表：

GPU 已可正常使用。

---

# nvidia-smi

成功輸出：

```
Driver Version

CUDA Version

GPU Name

GPU Memory

GPU Util

Power

Temperature

Processes
```

---

## Driver Version

```
580.159.04
```

代表：

GPU Driver 版本。

---

## CUDA Version

```
CUDA Version: 13.0
```

代表：

GPU Driver 支援最高 CUDA Version。

不是 Container 內 CUDA Runtime Version。

---

## GPU 型號

```
Tesla P100-PCIE-16GB
```

代表：

- Tesla Data Center GPU
- P100
- VRAM 16GB

---

## VRAM

```
0MiB / 16384MiB
```

代表：

```
目前使用量

/

GPU VRAM 總容量
```

VRAM：

GPU 專用記憶體。

不是：

CPU RAM。

---

## GPU Utilization

```
GPU-Util
```

代表：

GPU 核心目前運算使用率。

注意：

```
GPU Util

≠

VRAM 使用率
```

兩者互相獨立。

---

## GPU Power

```
29W / 250W
```

代表：

```
目前耗電

/

GPU 最大功耗(TDP)
```

AI Training 時：

Usage 會大幅提高。

---

## GPU Temperature

```
51°C
```

一般：

| 狀態 | 溫度 |
|------|------|
| Idle | 35~55°C |
| AI Training | 50~85°C |

若過高：

GPU 可能發生：

```
Thermal Throttling
```

---

## GPU Processes

```
Processes
```

可查看：

- Process Name
- PID
- GPU Memory Usage

常用於：

- GPU 被誰占用
- CUDA Out Of Memory
- GPU Utilization 排查

---

# 今天學到什麼

- GPU Quota
- GPU Stock
- GCE_STOCKOUT
- GPU Node Pool
- GPU Scheduling
- GPU Resource
- CUDA Image
- nvidia-smi
- Driver Version
- CUDA Version
- GPU Utilization
- VRAM
- GPU Power
- GPU Temperature
- GPU Processes

---

# 驗證

查看 GPU Node：

```bash
kubectl get nodes
```

查看 GPU Resource：

```bash
kubectl describe node <gpu-node>
```

查看 Pod：

```bash
kubectl get pod -o wide
```

進入 Pod：

```bash
kubectl exec -it gpu-test -n hpc-platform-dev -- bash
```

GPU：

```bash
nvidia-smi
```

---

# Troubleshooting

## 問題一

```
GCE_STOCKOUT
```

原因：

Google Cloud GPU 庫存不足。

---

## 問題二

```
GPU Resource 沒出現
```

確認：

```bash
kubectl describe node
```

是否出現：

```
nvidia.com/gpu: 1
```

---

## 問題三

Pod 無法排到 GPU Node

確認：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

是否存在。

---

# Interview

## Q1

GPU Quota 與 GPU Stock 有什麼差異？

**A：**

Quota 是 Project 可使用 GPU 上限；Stock 是 Cloud Provider 是否有 GPU 可提供，即使 Quota 足夠仍可能因 Stock 不足而建立失敗。

---

## Q2

為什麼只要宣告：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Pod 就會排到 GPU Node？

**A：**

Kubernetes Scheduler 會根據 Pod 宣告的 Resource Request（CPU、Memory、GPU）尋找符合條件的 Node，`nvidia.com/gpu: 1` 會使 Pod 僅能排程到具有 GPU Resource 的 Node。
