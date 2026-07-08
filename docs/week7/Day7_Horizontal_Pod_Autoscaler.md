# Week7 Day7 - Horizontal Pod Autoscaler (HPA)

## 今日平台增加什麼

今天平台完成 Kubernetes Horizontal Pod Autoscaler（HPA）。

利用：

* metrics-server
* CPU Metrics
* Resource Requests
* k6 壓力測試

成功讓 API Deployment 自動擴容與縮容。

---

# Platform Problem

假設 API 平時只有：

```text
1 Pod
```

突然有大量使用者：

```text
100

↓

500

↓

1000 Requests
```

如果仍然只有一個 Pod：

* CPU 使用率持續升高
* Response Time 增加
* 最後可能 Timeout

因此需要：

```text
Horizontal Pod Autoscaler
```

根據資源使用率，自動調整 Pod 數量。

---

# 今日知識鏈

```text
Client
      │
k6 Load Test
      │
API CPU Usage
      │
metrics-server
      │
Horizontal Pod Autoscaler
      │
Deployment
      │
ReplicaSet
      │
Pods
```

---

# HPA 與 Requests 的關係

API Deployment：

```yaml
resources:
  requests:
    cpu: "100m"
```

HPA：

```yaml
averageUtilization: 80
```

表示：

CPU 使用率：

```text
CPU Usage

÷

CPU Request
```

例如：

```text
CPU Usage = 90m

CPU Request = 100m

↓

90%
```

超過：

```text
80%
```

HPA 開始擴容。

---

# 驗證 metrics-server

確認：

```bash
kubectl top nodes
```

結果：

```text
CPU
Memory
```

正常顯示。

確認：

```bash
kubectl top pods -n hpc-platform
```

API：

```text
CPU: 3m

Memory: 58Mi
```

代表 metrics-server 正常提供 Metrics。

---

# 建立 HPA

建立：

```text
k8s/api-hpa.yaml
```

內容：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler

metadata:
  name: api-hpa
  namespace: hpc-platform

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api

  minReplicas: 1
  maxReplicas: 5

  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 80
```

部署：

```bash
kubectl apply -f k8s/api-hpa.yaml
```

查看：

```bash
kubectl get hpa -n hpc-platform
```

初始：

```text
TARGETS

3% / 80%

REPLICAS

1
```

---

# 使用 k6 壓力測試

建立：

```text
loadtest/benchmark.js
```

內容：

```javascript
import http from "k6/http";
import { sleep } from "k6";

export const options = {
  vus: 50,
  duration: "2m",
};

export default function () {
  http.post(
    "http://api.hpc.local/benchmark",
    JSON.stringify({
      benchmark: "cpu",
      simulate_failure: false,
    }),
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  sleep(0.1);
}
```

執行：

```bash
k6 run loadtest/benchmark.js
```

---

# 監控 HPA

另一個 Terminal：

```bash
kubectl get hpa -n hpc-platform -w
```

觀察：

```text
cpu: 3% / 80%

↓

cpu: 441% / 80%

↓

cpu: 499% / 80%
```

Deployment：

```text
Replicas

1

↓

4

↓

5
```

HPA 自動完成 Scale Out。

---

# Scale In

停止 k6：

```text
Ctrl + C
```

CPU 使用率下降。

HPA：

等待一段時間（Scale Down Stabilization）。

Deployment：

```text
5

↓

4

↓

3

↓

2

↓

1
```

自動完成 Scale In。

---

# 為什麼沒有立刻縮容？

Kubernetes 預設會等待一段時間。

避免：

```text
CPU

79%

↓

81%

↓

79%

↓

81%
```

造成：

```text
1 Pod

↓

2 Pods

↓

1 Pod

↓

2 Pods
```

不停震盪。

這就是：

```text
Scale Down Stabilization
```

---

# 平台架構

```text
Client
      │
Traefik
      │
Ingress
      │
Service
      │
Deployment
      │
Horizontal Pod Autoscaler
      │
ReplicaSet
      │
Pods (1~5)
```

---

# 今日重點

* HPA 根據 Metrics 自動調整 Pod 數量。
* CPU 使用率以 Requests 為基準計算。
* metrics-server 提供 CPU 與 Memory Metrics。
* k6 可快速建立 HTTP 壓力測試。
* HPA 可自動 Scale Out 與 Scale In。
* Scale Down 不會立即發生，以避免 Pod 數量震盪。

---

# Interview Q&A

## Q1：HPA 使用什麼資料決定是否擴容？

預設使用 metrics-server 提供的 CPU 或 Memory Metrics。

---

## Q2：HPA 的 CPU 使用率是如何計算的？

CPU Utilization = CPU Usage ÷ CPU Request。

因此 Deployment 必須設定 CPU Requests。

---

## Q3：為什麼停止壓測後沒有立即縮容？

Kubernetes 預設具有 Scale Down Stabilization 機制，避免 Pod 因負載波動而頻繁擴縮。

---

# Week7 成果

平台已完成：

* Deployment
* ConfigMap
* Secret
* Requests / Limits
* QoS
* Readiness Probe
* Liveness Probe
* Service（ClusterIP、NodePort）
* Traefik Ingress
* Host Routing
* Path Routing
* metrics-server
* Horizontal Pod Autoscaler
* k6 壓力測試
* Auto Scale Out / Scale In

平台已具備 Kubernetes 生產環境的重要基礎能力。

---

# 下一步

Week8：

GitOps Foundation

學習：

* Helm
* Kustomize
* GitOps
* Argo CD

將目前手動 `kubectl apply` 的部署方式，提升為企業常用的 GitOps 工作流程。

