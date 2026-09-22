<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day3 — Requests、limits 與 QoS

[上一課](<Day2_Secret.md>) · [本週目錄](README.md) · [下一課](<Day4_Liveness_and_Readiness_Probe.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史資源與 QoS 摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

此 API 設定 request 100m/128Mi、limit 500m/512Mi。QoS 判定要看整個 Pod，不能一般化成單一欄位不相等即全部判準；Guaranteed 也不保證免 OOM。排程採 requests，不代表無條件取得專用核心；「企業最常見」沒有本課證據。

## 程式／設定與來源

本次核對：[k8s/api-deployment.yaml](<../../k8s/api-deployment.yaml>)、[helm/api/values.yaml](<../../helm/api/values.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day3_Resource_Requests_Limits_QoS.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
QoS Class: Burstable
```

文內記載 Burstable，未保存 CPU throttling、OOM 或逐容器資源壓測；不能宣稱已完整驗證資源隔離。

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

# Week7 Day3 - Resource Requests, Limits and QoS

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)

---

## 今日平台增加什麼

今天平台新增 Kubernetes Resource Management。

API Pod 開始具備：

* CPU Requests
* Memory Requests
* CPU Limits
* Memory Limits

並了解 Kubernetes 如何根據 Requests、Limits 決定 Pod 的排程與 QoS（Quality of Service）。

---

# Platform Problem

如果 Pod 沒有設定資源需求：

```yaml
containers:
  - name: api
```

Kubernetes 不知道：

* 至少需要多少 CPU
* 至少需要多少 Memory
* 最多可以使用多少資源

結果可能造成：

* 單一 Pod 耗盡 Node CPU
* Memory OOM
* 其他 Pod 被影響
* Node 不穩定

---

# 今日知識鏈

```text
Node
   │
Scheduler
   │
Requests
   │
Pod
   │
Limits
   │
QoS
```

---

# Requests

Requests 表示：

> Pod 至少需要多少資源才能被排程。

本課程設定：

```yaml
requests:
  cpu: "100m"
  memory: "128Mi"
```

代表：

* CPU：0.1 Core
* Memory：128 MiB

Scheduler 必須找到符合條件的 Node。

---

# Limits

Limits 表示：

> Pod 最多可以使用多少資源。

設定：

```yaml
limits:
  cpu: "500m"
  memory: "512Mi"
```

代表：

* CPU 最多 0.5 Core
* Memory 最多 512 MiB

超過限制時：

CPU：

* 被 Linux CFS Throttle（限速）

Memory：

* 被 Kubernetes OOMKilled

---

# Hands-on

修改：

```text
k8s/api-deployment.yaml
```

新增：

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"

  limits:
    cpu: "500m"
    memory: "512Mi"
```

重新部署：

```bash
kubectl apply -f k8s/api-deployment.yaml

kubectl rollout status deployment api -n hpc-platform
```

驗證：

```bash
kubectl describe pod -n hpc-platform -l app=api
```

結果：

```text
Limits:
  cpu:     500m
  memory:  512Mi

Requests:
  cpu:     100m
  memory:  128Mi
```

---

# QoS（Quality of Service）

Kubernetes 依 Requests 與 Limits 將 Pod 分為三種等級。

## BestEffort

沒有設定任何 Resources。

```yaml
containers:
  - name: api
```

最容易在資源不足時被 OOM Kill。

---

## Burstable

Requests 與 Limits 不相同。

例如：

```yaml
requests:
  cpu: 100m
  memory: 128Mi

limits:
  cpu: 500m
  memory: 512Mi
```

本課程 API 使用此模式。

兼顧資源保證與彈性。

企業最常見。

---

## Guaranteed

Requests 與 Limits 完全相同。

例如：

```yaml
requests:
  cpu: 500m
  memory: 512Mi

limits:
  cpu: 500m
  memory: 512Mi
```

通常給：

* Database
* Kafka
* ZooKeeper
* 關鍵服務

提供最高優先保障。

---

# 驗證 QoS

執行：

```bash
kubectl describe pod <pod-name> -n hpc-platform
```

確認：

```text
QoS Class: Burstable
```

代表：

Requests ≠ Limits。

---

# 平台架構

```text
Node
 │
 ├── Scheduler
 │
 ▼
API Pod
 │
 ├── Requests
 │
 ├── Limits
 │
 └── QoS: Burstable
```

---

# 今日重點

* Requests 決定排程最低需求。
* Limits 決定 Pod 可使用的最大資源。
* CPU 超過 Limits 會被 Throttle。
* Memory 超過 Limits 會被 OOMKilled。
* QoS 由 Requests 與 Limits 決定。
* Burstable 是企業最常見的 QoS。

---

# Interview Q&A

## Q1：Requests 和 Limits 差在哪？

Requests 是 Scheduler 排程依據，代表最低保證。

Limits 是 Pod 可使用的最高資源限制。

---

## Q2：CPU 和 Memory 超過 Limits 的結果一樣嗎？

不一樣。

CPU：

* Throttle（限速）

Memory：

* OOMKilled（直接終止容器）

---

## Q3：什麼是 Burstable？

當 Requests 與 Limits 不相同時，Pod 的 QoS 為 Burstable。

能保證最低資源，同時允許在 Node 有餘裕時使用更多資源。

---

# 今日成果

API Pod 已具備完整的 Resource Management：

```text
Requests
      │
      ▼
Scheduler
      │
      ▼
Pod
      │
      ├── CPU Limit
      ├── Memory Limit
      └── QoS：Burstable
```

平台開始具備生產環境的資源管理能力。

---

# 下一步

Week7 Day4：

Liveness Probe、Readiness Probe 與 Kubernetes Self-healing。
