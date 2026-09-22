<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day7 — HPA 的作用範圍

[上一課](<Day6_Ingress_Traefik.md>) · [本週目錄](README.md) · [下一週](../week8/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 HPA 觀察。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

CPU 百分比相對 requests，499% 不是整機 499%。HPA 看指標與策略，並非超過80%立刻固定加一。此 HPA 只指 api Deployment，worker 模板固定1副本。k6 只提交 cpu 模擬分支，沒有驗證 benchmark 完成／結果或設定 checks thresholds。

## 程式／設定與來源

本次核對：[k8s/api-hpa.yaml](<../../k8s/api-hpa.yaml>)、[loadtest/benchmark.js](<../../loadtest/benchmark.js>)、[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day7_Horizontal_Pod_Autoscaler.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
cpu: 499% / 80%
```

舊文記載1→4→5再縮回1，缺時序原始監控、延遲與失敗率，不能稱 GPU／worker autoscaling 實测。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day7 - Horizontal Pod Autoscaler (HPA)

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-hpa.yaml](../../k8s/api-hpa.yaml)
- [loadtest/benchmark.js](../../loadtest/benchmark.js)：k6 API 壓測

---

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
