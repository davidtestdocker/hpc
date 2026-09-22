<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day1 — RBAC 與最小權限

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-pod-image-secret-security.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史RBAC HTTP狀態。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

benchmark-runner是教學讀取身分，主worker用api-jobset-runner可create JobSets及讀pods/log。測試curl只列HTTP碼沒有assert，Pod Completed不等於權限驗收通過；RBAC是加總權限，還需其他bindings背景。

## 程式／設定與來源

本次核對：[k8s/security/rbac-api-test.yaml](<../../k8s/security/rbac-api-test.yaml>)、[k8s/security/role.yaml](<../../k8s/security/role.yaml>)、[k8s/security/rolebinding.yaml](<../../k8s/security/rolebinding.yaml>)、[k8s/security/api-jobset-rbac.yaml](<../../k8s/security/api-jobset-rbac.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<day1-rbac-serviceaccount-least-privilege.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
HTTP 403
```

文內200/403支持當時allow/deny；未保存獨立完整log。本次不讀真實token／Secret。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
