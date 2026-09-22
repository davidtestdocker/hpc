<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day1 — RBAC 與最小權限

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-pod-image-secret-security.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

api-jobset-runner 的 Role 允許指定 JobSet 與 Pod／log 操作；RoleBinding 把權限給 ServiceAccount。API 認證成功不代表有任意刪除權，權限也不代表封包一定可達。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[k8s/security/api-jobset-rbac.yaml](<../../k8s/security/api-jobset-rbac.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
rules:
  # RBAC 規則適用的 API 群組；空字串代表核心 API。
  - apiGroups:
      - jobset.x-k8s.io
    # 資源設定；Pod 中是 requests／limits，Kustomize 中是待組合的檔案清單。
    resources:
      - jobsets
    # 允許的 API 動作，例如 get、list、create。
    verbs:
      - get
      - list
      - watch
      - create
  # Completion collector 只需列出 launcher Pod 並讀取 log，不允許修改或刪除 Pod。
  - apiGroups:
      - ""
    resources:
      - pods
      - pods/log
    verbs:
      - get
      - list
---
apiVersion: rbac.authorization.k8s.io/v1
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day1-rbac-serviceaccount-least-privilege.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week20 Day1 — RBAC / ServiceAccount / Least Privilege

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/security/rbac-api-test.yaml](../../k8s/security/rbac-api-test.yaml)
- [k8s/security/role.yaml](../../k8s/security/role.yaml)
- [k8s/security/rolebinding.yaml](../../k8s/security/rolebinding.yaml)
- [k8s/security/serviceaccount.yaml](../../k8s/security/serviceaccount.yaml)

---

## 今日完成

完成 Kubernetes workload 身分與最小權限控制：

    ServiceAccount
    ↓
    Role
    ↓
    RoleBinding
    ↓
    Kubernetes API

並驗證：

    需要的權限 → allow
    不需要的權限 → deny

---

## 1. ServiceAccount

ServiceAccount 是：

    Pod 在 Kubernetes 裡的身分

建立：

    benchmark-runner

Pod 使用：

    serviceAccountName: benchmark-runner

之後 Pod 呼叫 Kubernetes API 時，
會以這個 identity 進行 authentication。

---

## 2. RBAC

RBAC：

    Role-Based Access Control

控制：

    Who
    ↓
    Which Resource
    ↓
    Which Verb

例如：

    benchmark-runner
    ↓
    pods
    ↓
    get / list / watch

---

## 3. Least Privilege

原則：

    只給 workload 真正需要的權限

本次 benchmark-runner 只需要讀取：

    Pods
    Jobs

因此允許：

    get
    list
    watch

不允許：

    create
    update
    patch
    delete
    secrets access
    cluster-wide resources

---

## 4. Role

建立：

    benchmark-reader

Namespace：

    hpc-platform-dev

允許：

    pods:
      get
      list
      watch

    jobs:
      get
      list
      watch

Role 本身只是：

    權限規則

還沒有指定誰可以使用。

---

## 5. RoleBinding

建立：

    benchmark-reader-binding

把：

    ServiceAccount:
    benchmark-runner

綁到：

    Role:
    benchmark-reader

因此：

    benchmark-runner
    ↓
    benchmark-reader permissions
    ↓
    only in hpc-platform-dev

---

## 6. kubectl auth 驗證

允許：

    get pods
    → yes

    list jobs
    → yes

拒絕：

    delete pods
    → no

    get secrets
    → no

證明：

    read-only workload permissions
    正常生效

---

## 7. 真實 Pod API 驗證

建立：

    rbac-api-test

Pod 使用：

    serviceAccountName: benchmark-runner

Pod 內會自動取得：

    ServiceAccount token
    CA certificate

並直接呼叫：

    https://kubernetes.default.svc

流程：

    Pod
    ↓
    ServiceAccount Token
    ↓
    API Server Authentication
    ↓
    RBAC Authorization

---

## 8. API 驗證結果

GET Pods：

    HTTP 200

代表：

    pods read permission
    → allowed

GET Secrets：

    HTTP 403

代表：

    secrets permission
    → denied

DELETE Pod：

    HTTP 403

代表：

    pod delete permission
    → denied

這是真正從 workload 內部驗證 RBAC，
不是只有 kubectl auth 模擬。

---

## 9. Role vs ClusterRole

Role：

    namespace-scoped permission

例如：

    hpc-platform-dev
    裡面的 pods/jobs read

ClusterRole：

    cluster-scoped resource permission
    或可重用的 permission template

例如：

    nodes
    namespaces
    cluster-wide controllers

---

## 10. Binding 差異

Role + RoleBinding：

    namespace-scoped permission

ClusterRole + RoleBinding：

    使用共用 ClusterRole 規則
    但只在該 namespace 生效

ClusterRole + ClusterRoleBinding：

    cluster-wide permission

Production 上應避免：

    workload
    → cluster-admin

除非真的有必要。

---

## 11. Namespace Boundary 驗證

benchmark-runner 在：

    hpc-platform-dev

可以：

    get pods
    → yes

但在：

    default namespace

結果：

    get pods
    → no

代表 RoleBinding 沒有跨 namespace。

---

## 12. Cluster Scope 驗證

測試：

    get nodes

結果：

    no

Node 是：

    cluster-scoped resource

因此證明：

    benchmark-runner
    沒有 cluster-wide permission

---

## 13. 最終權限模型

    Pod
    ↓
    ServiceAccount
    benchmark-runner
    ↓
    RoleBinding
    ↓
    Role
    benchmark-reader
    ↓
    hpc-platform-dev only
    ↓
    Pods / Jobs
    get / list / watch

拒絕：

    Secrets
    Pod delete
    Other namespaces
    Nodes
    Cluster-wide operations

---

## 14. Repo

    k8s/security/
    ├─ serviceaccount.yaml
    ├─ role.yaml
    ├─ rolebinding.yaml
    └─ rbac-api-test.yaml

---

## Interview Review

**Q1：ServiceAccount、Role、RoleBinding 分別負責什麼？**  
A：ServiceAccount 是 Pod 的 Kubernetes identity；Role 定義 namespace 內允許的資源與操作；RoleBinding 把 Role 權限授予指定的 User、Group 或 ServiceAccount。

**Q2：為什麼 production workload 不應直接綁 cluster-admin？**  
A：違反 least privilege。若 workload 被入侵，攻擊者可能讀取 Secrets、刪除其他 workloads 或控制整個 cluster，因此應只授予實際需要的最小權限。
