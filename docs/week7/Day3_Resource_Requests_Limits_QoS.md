<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day3 — Requests、limits 與 QoS

[上一課](<Day2_Secret.md>) · [本週目錄](README.md) · [下一課](<Day4_Liveness_and_Readiness_Probe.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

requests 影響 Pod 是否可排入節點，CPU limit 可能節流，memory limit 可能導致 OOM。降低 request 只能改排程宣告，不會讓真實資源消耗自動降低。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/values.yaml](<../../helm/api/values.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
resources:
  # 排程器計算需求時採用的資源量；500m CPU 等於 0.5 顆核心。
  requests:
    # CPU 數量：1 代表一顆核心，m 表示千分之一核心。
    cpu: "100m"
    # 記憶體容量；Mi／Gi 是以 1024 為基底的單位。
    memory: "128Mi"
  # 容器可使用的資源上限；GPU 份額的實際意義取決於裝置外掛設定。
  limits:
    cpu: "500m"
    memory: "512Mi"
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

# This is to setup the liveness and readiness probes more information can be found here: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
# 存活探針失敗達門檻時，kubelet 會重啟容器。
```

## 已有結果與解讀

### CPU 叢集重建：已保存的驗收結果

日期：2026-09-21。環境：隔離 CPU-only GKE 重建驗收；不是主環境的多 GPU 實驗。該次叢集已清理，讀這份結果不需要重新建立。

```json
{
  "recorded_at": "2026-09-21",
  "scope": "fresh CPU-only GKE bootstrap and platform acceptance; excludes GPU and MPI execution",
  "result": "pass",
  "terraform": {
    "apply": "3 added",
    "post_apply_plan": "No changes",
    "destroy": "3 destroyed",
    "state_resources_after_destroy": 0,
    "cluster_lookup_after_destroy": "404 Not Found"
  },
  "controllers": {
    "jobset": "v0.12.0 Ready on system-pool with 100m CPU request",
    "kueue": "v0.19.2 Ready on system-pool with Recreate deployment strategy"
  },
  "platform": {
    "api": "Running on system-pool; /health healthy",
    "redis": "Running on system-pool; connected; PVC Bound",
    "postgres": "Running on system-pool; jobs table query succeeded; PVC Bound",
    "overlay_diff_after_apply": "empty"
  },
  "security": {
    "postgres_secret": "created from external env file; value not captured",
    "mpi_ssh_key": "generated in temporary directory; value not captured",
    "api_service_account_create_jobsets": "yes",
    "api_service_account_delete_pods": "no"
  },
  "limitations": [
    "gpu-pool had zero nodes because project-wide GPU quota was exhausted",
    "no MPI workload was submitted in this CPU-only rehearsal",
    "database initialization used create_all rather than schema migration"
  ]
}
```

解讀：Terraform 建立 3 個資源、無 drift，JobSet／Kueue controllers 和 API／Redis／DB 驗收成功；create JobSet 權限允許，delete Pod 權限拒絕。最後 destroy 3、state 空、cluster 查詢 404，證明當次隔離叢集已刪除。**不包含 GPU 或 MPI 執行驗收**，也不是所有雲端資源的停費證明。

來源：[原始 CPU bootstrap JSON](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day3_Resource_Requests_Limits_QoS.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
