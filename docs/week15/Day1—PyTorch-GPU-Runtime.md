# Week15 Day1 — PyTorch GPU Runtime

## 今日目標

在既有的 **HPC AI Performance Engineering Platform** 上新增 PyTorch GPU Runtime Capability。

今天不是建立第二套平台，而是沿用既有：

```text
Git
 ↓
ArgoCD
 ↓
Kustomize
 ↓
Helm
 ↓
Kubernetes
 ↓
GPU Node
 ↓
PyTorch + CUDA
```

Day1 最終目標：

```text
PyTorch
 ↓
CUDA Runtime
 ↓
NVIDIA Driver
 ↓
Tesla P100
 ↓
GPU Computation
```

並由 Kubernetes / GitOps 正式管理 Runtime。

---

# 1. Day1 架構

Week1～14 已建立：

```text
HPC AI Performance Engineering Platform
├── GKE
├── Kubernetes
├── Helm
├── Kustomize
├── ArgoCD
├── Prometheus
├── Grafana
├── NVIDIA GPU Node
├── NVIDIA Device Plugin
└── DCGM Exporter
```

Week15 Day1 在既有平台新增：

```text
HPC AI Platform
      │
      ▼
PyTorch Runtime
      │
      ├── PyTorch
      ├── CUDA
      ├── GPU Scheduling
      ├── GPU Compute
      └── Runtime Logging
```

完整部署流程：

```text
runtime/pytorch/runtime.py
            │
            ▼
         Git Push
            │
            ▼
          ArgoCD
            │
            ▼
        Kustomize
         │      │
         │      └── configMapGenerator
         │                   │
         │                   ▼
         │          pytorch-runtime-code
         │
         └── Helm
              │
              ▼
      pytorch-runtime Deployment
              │
              ▼
     Official PyTorch Image
              │
              ▼
         PyTorch + CUDA
              │
              ▼
          Tesla P100
```

---

# 2. PyTorch Runtime 程式

目錄：

```text
runtime/
└── pytorch/
    ├── __init__.py
    └── runtime.py
```

`runtime/pytorch/runtime.py`：

```python
import time
import torch


def validate_runtime():
    # Verify that PyTorch can access CUDA
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    # Get the GPU assigned to this runtime
    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(device)

    # Run a small GPU computation to verify CUDA execution
    a = torch.randn((2048, 2048), device=device)
    b = torch.randn((2048, 2048), device=device)
    c = torch.matmul(a, b)

    # Wait until the GPU computation is completed
    torch.cuda.synchronize()

    print("PyTorch Runtime Ready")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"GPU Device: {gpu_name}")
    print(f"Result Device: {c.device}")


def main():
    # Validate the runtime when the container starts
    validate_runtime()

    # Keep the runtime process alive
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
```

---

# 3. Runtime Validation 做了什麼？

## CUDA 驗證

```python
torch.cuda.is_available()
```

確認：

```text
PyTorch
 ↓
CUDA Runtime
 ↓
NVIDIA Driver
 ↓
GPU
```

整條路徑正常。

如果 CUDA 無法使用：

```python
raise RuntimeError("CUDA is not available")
```

Runtime 直接失敗，不讓錯誤環境繼續執行。

---

## GPU Device

```python
device = torch.device("cuda:0")
```

`cuda:0` 表示：

```text
cuda
 ↓
CUDA Device

0
 ↓
Container 可使用的第 1 張 GPU
```

取得 GPU 名稱：

```python
gpu_name = torch.cuda.get_device_name(device)
```

實際環境：

```text
Tesla P100-PCIE-16GB
```

---

## GPU Tensor

```python
a = torch.randn((2048, 2048), device=device)
b = torch.randn((2048, 2048), device=device)
```

因為：

```python
device=device
```

Tensor 直接建立在：

```text
GPU VRAM
```

而不是 CPU RAM。

---

## GPU Computation

```python
c = torch.matmul(a, b)
```

實際流程：

```text
Python
 ↓
PyTorch
 ↓
CUDA Kernel
 ↓
Tesla P100
 ↓
Matrix Multiplication
```

所以 Day1 不只是「看到 GPU」。

而是已經真正執行 GPU workload。

---

# 4. torch.cuda.synchronize()

程式：

```python
torch.cuda.synchronize()
```

CUDA operation 通常是 asynchronous。

例如：

```text
CPU
 │
 ├── Launch GPU Work
 │
 └── Continue
```

CPU 將工作送給 GPU 後，不一定等待 GPU 做完。

加入：

```python
torch.cuda.synchronize()
```

變成：

```text
CPU
 │
 ├── Launch GPU Work
 │
 ▼
Wait
 │
 ▼
GPU Finish
 │
 ▼
CPU Continue
```

因此：

```text
torch.cuda.synchronize()
```

代表：

> 等待目前 GPU 工作完成。

不是清除 VRAM。

---

# 5. PyTorch Runtime Helm Chart

建立：

```text
helm/
└── pytorch-runtime/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        └── deployment.yaml
```

---

## Chart.yaml

```yaml
apiVersion: v2
name: pytorch-runtime
description: PyTorch GPU Runtime for HPC AI Platform
type: application
version: 0.1.0
appVersion: "2.12.0"
```

---

## values.yaml

```yaml
replicaCount: 1

image:
  repository: pytorch/pytorch
  tag: 2.12.0-cuda12.6-cudnn9-runtime
  pullPolicy: IfNotPresent

gpu:
  count: 1

nodeSelector:
  cloud.google.com/gke-nodepool: gpu-pool
```

---

# 6. 為什麼使用官方 PyTorch Image？

使用：

```text
pytorch/pytorch:2.12.0-cuda12.6-cudnn9-runtime
```

Image 已經包含：

```text
Python
PyTorch
CUDA Runtime
cuDNN
```

所以 Day1 不需要重新：

```text
Dockerfile
 ↓
docker build
 ↓
Artifact Registry
 ↓
Kubernetes
```

目前真正缺的是：

```text
runtime.py
```

因此 Day1 使用：

```text
Official PyTorch Image
        +
runtime.py
        ↓
PyTorch Runtime
```

---

# 7. Runtime Code 如何進入 Container？

原始程式：

```text
runtime/pytorch/runtime.py
```

Kustomize：

```yaml
configMapGenerator:
  - name: pytorch-runtime-code
    files:
      - runtime.py=../../../runtime/pytorch/runtime.py

generatorOptions:
  disableNameSuffixHash: true
```

流程：

```text
runtime.py
   ↓
Kustomize
   ↓
ConfigMap
pytorch-runtime-code
   ↓
Volume
   ↓
Container
```

Deployment：

```yaml
volumeMounts:
  - name: runtime-code
    mountPath: /runtime
    readOnly: true

volumes:
  - name: runtime-code
    configMap:
      name: pytorch-runtime-code
```

因此 Container 裡會出現：

```text
/runtime/runtime.py
```

---

# 8. Runtime Entry Point

Deployment：

```yaml
command:
  - python

args:
  - -u
  - /runtime/runtime.py
```

實際相當於：

```bash
python -u /runtime/runtime.py
```

Pod 一啟動就執行 Runtime Validation。

不再像之前：

```text
sleep infinity
 ↓
kubectl exec
 ↓
手動進 Python
```

Day1 前：

```text
GPU Sandbox
```

Day1 後：

```text
Platform Managed Runtime
```

---

# 9. 為什麼使用 python -u？

一開始執行：

```bash
kubectl logs deployment/pytorch-runtime \
  -n hpc-platform-dev
```

沒有看到輸出。

原因是 Python stdout buffering。

加入：

```text
-u
```

代表：

```text
Unbuffered stdout / stderr
```

讓：

```python
print(...)
```

立即送到 Container stdout。

因此 Kubernetes 可以立即收集 Log。

---

# 10. Kubernetes GPU Resource

Runtime 宣告：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

意思：

```text
這個 Container
需要
1 張 GPU
```

NVIDIA Device Plugin 將 GPU 暴露成 Kubernetes Extended Resource：

```text
nvidia.com/gpu
```

Scheduler 因此知道：

```text
pytorch-runtime
      ↓
需要 GPU Node
```

---

# 11. GPU NodeSelector

設定：

```yaml
nodeSelector:
  cloud.google.com/gke-nodepool: gpu-pool
```

代表：

```text
pytorch-runtime
      ↓
只能排到
      ↓
gpu-pool
```

避免 AI workload 被排到一般 CPU Node。

---

# 12. GPU Taint / Toleration

GPU Node 有：

```text
nvidia.com/gpu=present:NoSchedule
```

作用：

```text
普通 Pod
   ↓
不能隨便進 GPU Node
```

PyTorch Runtime 加：

```yaml
tolerations:
  - key: nvidia.com/gpu
    operator: Equal
    value: present
    effect: NoSchedule
```

代表：

```text
PyTorch Runtime
      ↓
允許進入 GPU Node
```

---

# 13. GPU Scheduling 三個重要設定

```text
resources:
  nvidia.com/gpu: 1
```

代表：

> 我要 1 張 GPU。

```text
nodeSelector
```

代表：

> 我要去 gpu-pool。

```text
toleration
```

代表：

> 我允許被排到有 GPU Taint 的 Node。

完整：

```text
PyTorch Pod
    │
    ├── GPU Request
    │
    ├── NodeSelector
    │
    └── Toleration
            │
            ▼
     Kubernetes Scheduler
            │
            ▼
         gpu-pool
            │
            ▼
       Tesla P100
```

---

# 14. Helm 整合進既有 Kustomize

原本平台：

```text
kustomize/
└── overlays/
    └── dev/
        └── kustomization.yaml
```

新增：

```yaml
- name: pytorch-runtime
  releaseName: pytorch-runtime
  namespace: hpc-platform-dev
  includeCRDs: false
```

因此仍然只有：

```text
ArgoCD Application
hpc-dev
```

沒有第二套：

```text
ArgoCD
CI/CD
Kustomize
```

---

# 15. Helm Render 驗證

先驗證 Helm：

```bash
helm template pytorch-runtime ./helm/pytorch-runtime
```

目的：

```text
Helm Template
 ↓
Render Kubernetes YAML
 ↓
確認 Template 語法正確
```

---

# 16. Kustomize Render 驗證

完整 Render：

```bash
kubectl kustomize \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
  kustomize/overlays/dev > /tmp/dev.yaml
```

查看 Runtime：

```bash
grep -A45 "name: pytorch-runtime" /tmp/dev.yaml
```

成功確認：

```text
ConfigMap
└── pytorch-runtime-code

Deployment
└── pytorch-runtime
```

Deployment 最終包含：

```text
Official PyTorch Image
GPU Resource
NodeSelector
Toleration
ConfigMap Volume
Runtime Entry Point
```

---

# 17. GitOps Deployment

修改完成後：

```bash
git add runtime/pytorch/runtime.py \
        helm/pytorch-runtime \
        kustomize/overlays/dev/kustomization.yaml
```

Commit：

```bash
git commit -m "feat: add PyTorch GPU runtime"
```

Push：

```bash
git push origin master
```

之後：

```text
Git
 ↓
ArgoCD Auto Sync
 ↓
Kustomize
 ↓
Helm
 ↓
Kubernetes
 ↓
pytorch-runtime
```

不用手動：

```bash
kubectl apply
```

因為 Git 是 Source of Truth。

---

# 18. Deployment 更新時遇到 GPU Pending

更新 Runtime 後出現：

```text
pytorch-runtime-old    Running
pytorch-runtime-new    Pending
```

原因不是 PyTorch。

而是：

```text
GPU 數量 = 1
```

舊 Pod：

```text
Old Pod
 ↓
P100 × 1
```

已經吃掉唯一 GPU。

Deployment 預設：

```text
RollingUpdate
```

流程：

```text
Create New Pod
      ↓
Wait New Pod Ready
      ↓
Delete Old Pod
```

但是：

```text
Old Pod
 ↓
GPU × 1

New Pod
 ↓
需要 GPU × 1

Available GPU
 ↓
0
```

所以：

```text
New Pod = Pending
```

---

# 19. Recreate Strategy

解法：

```yaml
strategy:
  type: Recreate
```

更新流程變成：

```text
Old Pod
 ↓
Delete
 ↓
Release GPU
 ↓
New Pod
 ↓
Allocate GPU
 ↓
Running
```

目前環境：

```text
Runtime Replica = 1
GPU = 1
```

因此使用：

```text
Recreate
```

可以避免單 GPU 環境下 RollingUpdate 發生 GPU Resource Deadlock。

這是 Day1 很重要的 Kubernetes GPU 實務問題。

---

# 20. Runtime 最終驗證

Pod：

```bash
kubectl get pods -n hpc-platform-dev
```

成功：

```text
pytorch-runtime-xxxxxxxxxx-xxxxx   1/1   Running
```

查看 Logs：

```bash
kubectl logs deployment/pytorch-runtime \
  -n hpc-platform-dev
```

實際結果：

```text
PyTorch Runtime Ready
PyTorch Version: 2.12.0+cu126
CUDA Available: True
GPU Device: Tesla P100-PCIE-16GB
Result Device: cuda:0
```

---

# 21. 這些 Log 分別證明什麼？

```text
PyTorch Runtime Ready
```

代表 Runtime validation 完成。

```text
PyTorch Version: 2.12.0+cu126
```

代表：

```text
PyTorch 2.12
+
CUDA 12.6 Runtime
```

```text
CUDA Available: True
```

代表：

```text
PyTorch
 ↓
CUDA
 ↓
NVIDIA Driver
```

路徑正常。

```text
GPU Device: Tesla P100-PCIE-16GB
```

代表 Container 成功取得實體 GPU。

```text
Result Device: cuda:0
```

代表 Matrix Multiplication 的結果真正存在 GPU。

因此不是只有 GPU detection。

而是：

```text
GPU Detection
+
GPU Memory Allocation
+
GPU Computation
```

全部成功。

---

# 22. Day1 前後差異

## Day1 前

```text
pytorch-gpu Pod
      ↓
sleep infinity
      ↓
kubectl exec
      ↓
python
      ↓
人工測試 CUDA
```

用途：

```text
GPU Sandbox / Debug
```

---

## Day1 後

```text
Git
 ↓
ArgoCD
 ↓
Kustomize + Helm
 ↓
Kubernetes Deployment
 ↓
PyTorch Runtime
 ↓
Automatic CUDA Validation
 ↓
GPU Computation
 ↓
Kubernetes Logs
```

用途：

```text
Platform Managed AI Runtime
```

---

# 23. Day1 最重要觀念

## PyTorch / CUDA 關係

```text
PyTorch
 ↓
CUDA Runtime
 ↓
NVIDIA Driver
 ↓
GPU
```

PyTorch 本身不是直接控制 GPU。

PyTorch 透過 CUDA 使用 NVIDIA GPU。

---

## cuda:0

```text
cuda:0
```

表示：

```text
Container 可使用的第一張 CUDA GPU
```

不是：

```text
GKE 第 0 台機器
```

也不是：

```text
整個 Cluster 的 GPU ID
```

---

## GPU 是 Kubernetes Resource

```yaml
nvidia.com/gpu: 1
```

GPU 跟：

```text
CPU
Memory
```

一樣可以被 Kubernetes Scheduler 管理。

但 GPU 是 Extended Resource。

---

## Training / Runtime / Deployment Lifecycle 不一定相同

Day1 Runtime Validation：

```text
Deployment
```

因為目前 Runtime 保持常駐。

後續 Training：

```text
Kubernetes Job
```

因為 Training 是：

```text
Start
 ↓
Train
 ↓
Finish
 ↓
Exit
```

不同 workload 應使用符合生命週期的 Kubernetes Controller。

---

# 24. 常用指令複習

查看 Runtime Pod：

```bash
kubectl get pods -n hpc-platform-dev
```

查看 Runtime Logs：

```bash
kubectl logs deployment/pytorch-runtime \
  -n hpc-platform-dev
```

查看 Runtime Deployment：

```bash
kubectl get deployment pytorch-runtime \
  -n hpc-platform-dev
```

查看排程 Node：

```bash
kubectl get pod \
  -n hpc-platform-dev \
  -l app=pytorch-runtime \
  -o wide
```

Helm Render：

```bash
helm template pytorch-runtime ./helm/pytorch-runtime
```

Kustomize Render：

```bash
kubectl kustomize \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
  kustomize/overlays/dev
```

---

# 25. Day1 最終成果

完成：

```text
Existing HPC AI Platform
          │
          ▼
PyTorch GPU Runtime
          │
          ├── Official PyTorch Image
          ├── CUDA Runtime
          ├── GPU Resource Request
          ├── GPU Node Scheduling
          ├── ConfigMap Runtime Code
          ├── Helm Deployment
          ├── Kustomize Integration
          ├── ArgoCD GitOps
          ├── GPU Compute Validation
          └── Kubernetes Logging
```

實際環境：

```text
PyTorch = 2.12.0+cu126
CUDA Available = True
GPU = Tesla P100-PCIE-16GB
Result Device = cuda:0
```

---

# Day1 一句話複習

```text
Week15 Day1 將原本人工 kubectl exec 的 PyTorch GPU 測試，
正式整合成由 GitOps 管理、Kubernetes 排程，
並能自動驗證 PyTorch → CUDA → NVIDIA GPU 計算路徑的 AI Runtime。
```

---

# Interview

## Q1：為什麼單 GPU Deployment 使用 RollingUpdate 可能讓新 Pod 一直 Pending？

Deployment 預設會先建立新 Pod，再刪除舊 Pod。

如果：

```text
GPU = 1
```

而舊 Pod 已經佔用 GPU，新 Pod 又要求：

```yaml
nvidia.com/gpu: 1
```

Scheduler 找不到剩餘 GPU，因此新 Pod 會一直 Pending。

單 GPU 開發環境可以使用：

```yaml
strategy:
  type: Recreate
```

先刪除舊 Pod 釋放 GPU，再建立新版 Pod。

---

## Q2：Kubernetes Pod 如何讓 PyTorch 使用實體 NVIDIA GPU？

Pod 宣告：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

完整流程：

```text
Pod
 ↓
GPU Resource Request
 ↓
Kubernetes Scheduler
 ↓
GPU Node
 ↓
NVIDIA Device Plugin
 ↓
Container
 ↓
PyTorch
 ↓
CUDA Runtime
 ↓
NVIDIA Driver
 ↓
Tesla P100
```

PyTorch 再透過：

```python
torch.cuda.is_available()
```

確認 CUDA 可用，並透過：

```python
torch.cuda.get_device_name(0)
```

取得實際 GPU。
