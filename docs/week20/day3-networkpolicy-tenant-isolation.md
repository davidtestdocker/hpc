<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day3 — NetworkPolicy 與隔離

[上一課](<day2-pod-image-secret-security.md>) · [本週目錄](README.md) · [下一課](<day4-ha-node-failure-recovery.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

policy 用 selector 選流量對象，需要 CNI enforcement 才能阻擋。隔離 Calico 已測 baseline／allow／deny／recovery，主 GKE enforcement 仍關閉，不得寫成所有 tenant 已隔離。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[k8s/security/network-policy/allow-client-to-server.yaml](<../../k8s/security/network-policy/allow-client-to-server.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  ingress:
    - from:
        - podSelector:
            matchLabels:
              access: allowed
      ports:
        - protocol: TCP
          port: 8080
```

## 已有結果與解讀

### NetworkPolicy：已保存封包驗證結果

日期：2026-09-21。環境：隔離 `hpc-gpu-sg-rehearsal`，Calico、CPU-only；此叢集已在該次驗收後刪除。

```json
{
  "environment": {
    "cluster": "hpc-gpu-sg-rehearsal",
    "zone": "asia-southeast1-a",
    "lifecycle": "terraform apply then destroy",
    "network_policy": {
      "enabled": true,
      "provider": "CALICO"
    },
    "system_node": {
      "count": 1,
      "machine_type": "e2-standard-2",
      "ready": true
    },
    "gpu_node_count": 0
  },
  "test": {
    "namespace": "network-policy-validation",
    "server": "server:80",
    "policy": "allow-labeled-client-to-server",
    "baseline": {
      "allowed_client_exit_code": 0,
      "denied_client_exit_code": 0
    },
    "with_policy": {
      "allowed_client_exit_code": 0,
      "denied_client_exit_code": 1,
      "denied_client_output": "wget: download timed out"
    },
    "after_policy_delete": {
      "denied_client_exit_code": 0
    }
  },
  "cleanup": {
    "terraform": "0 added, 0 changed, 3 destroyed",
    "state_resources_after_destroy": 0,
    "gke_describe_after_destroy": "404 Not Found"
  },
  "result": "pass"
}
```

解讀：policy 前兩個 client 都成功；套用後 allowed 成功、denied timeout；移除 policy 後 denied 恢復。這支持該次隔離叢集的 ingress 規則有效，**主 hpc-gpu-sg enforcement 仍關閉**。不需要你再開 VM 重測。

來源：[原始 NetworkPolicy JSON](<../evidence/network-policy-validation-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day3-networkpolicy-tenant-isolation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week20 Day3 — NetworkPolicy / Tenant Isolation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/security/network-policy/allow-dns.yaml](../../k8s/security/network-policy/allow-dns.yaml)
- [k8s/security/network-policy/allow-same-namespace.yaml](../../k8s/security/network-policy/allow-same-namespace.yaml)
- [k8s/security/network-policy/default-deny.yaml](../../k8s/security/network-policy/default-deny.yaml)

---

## 今日完成

建立 Kubernetes multi-tenant network isolation policy：

    Default Deny
        ↓
    Explicit Allow
        ↓
    DNS Allow
    +
    Same-Namespace Allow

Repo：

    k8s/security/network-policy/
    ├─ default-deny.yaml
    ├─ allow-dns.yaml
    └─ allow-same-namespace.yaml

---

## 1. Namespace 不等於 Network Isolation

Namespace 是：

    logical boundary

但預設不代表：

    Team A Pod
    X
    Team B Pod

如果網路路由允許，不同 namespace Pod 仍可能互相連線。

真正限制 Pod-to-Pod traffic：

    NetworkPolicy

---

## 2. Tenant Isolation

假設：

    team-a
    ├─ training
    └─ api

    team-b
    ├─ training
    └─ api

目標：

    team-a → team-a ✅
    team-b → team-b ✅

    team-a → team-b ❌
    team-b → team-a ❌

只有明確需要的 cross-tenant traffic 才另外 allow。

---

## 3. Ingress / Egress

Ingress：

    外部 → 我的 Pod

Egress：

    我的 Pod → 外部

例如：

    Pod A → Pod B

如果雙方都有 NetworkPolicy：

    A Egress 必須允許
    +
    B Ingress 必須允許

traffic 才能成立。

---

## 4. Default Deny

建立：

    default-deny

設定：

    podSelector: {}

代表：

    選擇 namespace 裡全部 Pods

PolicyTypes：

    Ingress
    Egress

沒有 allow rules，因此：

    ingress → default deny
    egress  → default deny

Production 常見原則：

    deny by default
    ↓
    explicit allow

---

## 5. Allow DNS

Default Deny 會連 DNS egress 一起擋掉。

因此加入：

    allow-dns

允許：

    hpc-platform-dev Pods
        ↓
    kube-system
        ↓
    UDP 53
    TCP 53

讓 workload 可以解析：

    Service DNS
    Kubernetes DNS
    internal hostnames

---

## 6. Allow Same Namespace

建立：

    allow-same-namespace

Ingress：

    podSelector: {}

Egress：

    podSelector: {}

單獨使用 podSelector 時，
Pod selection 限制在 NetworkPolicy 所在 namespace。

因此：

    hpc-platform-dev Pod
    ↔
    hpc-platform-dev Pod
    ✅

其他 namespace：

    → hpc-platform-dev
    ❌

---

## 7. Policy 是 Additive

NetworkPolicy allow rules 是累加的。

目前：

    default-deny
    +
    allow-dns
    +
    allow-same-namespace

最終允許：

    Same namespace communication ✅
    DNS TCP/UDP 53              ✅

其他未明確允許：

    ❌

不是後面的 policy 把前面的 policy 覆蓋掉。

---

## 8. Multi-Tenant Security Layers

完整 isolation 不只靠 NetworkPolicy。

    ServiceAccount + RBAC
    → API identity / permission isolation

    Pod Security
    → runtime privilege isolation

    NetworkPolicy
    → network isolation

    Kueue
    → GPU quota / resource isolation

    Priority / Preemption
    → scheduling policy

組合後才形成較完整的：

    Multi-Tenant AI Cluster

---

## 9. GPU Cluster Example

Training workload 可以被限制為：

    DNS                         ✅
    Same-team service           ✅
    Required metrics endpoint   ✅

但：

    Other tenant Pods           ❌
    Other tenant database       ❌
    Random internal service     ❌

核心思想：

    Network Least Privilege

只允許 workload 真正需要的 traffic。

---

## 10. 2026-09-21 實測與主環境邊界

目前 hpc-gpu-sg：

    addonsConfig:
      networkPolicyConfig:
        disabled: true

代表主 `hpc-gpu-sg` 仍沒有啟用 NetworkPolicy enforcement。沒有直接在主叢集
套用 policy，避免把 API 接受 manifest 誤當成封包隔離成功。

另由 Terraform 建立 CPU-only 隔離叢集 `hpc-gpu-sg-rehearsal`，GKE API
回報 `networkPolicy.enabled=true`、provider `CALICO`。在獨立 namespace
部署 server、allowed client 與 denied client 後，結果如下：

    policy 前：allowed client → server  ✅
    policy 前：denied client → server   ✅
    policy 後：allowed client → server  ✅
    policy 後：denied client → timeout  ✅
    移除 policy：denied client 恢復     ✅

測試使用 [fixtures](../../k8s/security/network-policy/rehearsal-fixtures.yaml)、
[allow policy](../../k8s/security/network-policy/allow-client-to-server.yaml)，
結構化結果見 [evidence JSON](../evidence/network-policy-validation-20260921.json)。
驗收後 Terraform 完成 3-resource destroy，state 為空且 GKE 查詢回傳 404。

這證明隔離 Calico GKE 的 ingress allow／deny enforcement，不代表主叢集已啟用、
全平台 policy 已設計完成，或 egress／跨 namespace／DNS 規則也已實測。

---

## Interview Review

**Q1：Kubernetes Namespace 是否會自動隔離不同 namespace 的 Pod 網路？**  
A：不會。Namespace 主要是邏輯與資源管理邊界；Pod 網路隔離需要支援 NetworkPolicy enforcement 的 CNI，再透過 default deny 與 explicit allow 建立 traffic policy。

**Q2：Default Deny 後為什麼通常要另外允許 DNS？**  
A：因為 Egress Default Deny 也會阻止 Pod 對 DNS server 的流量，造成 Service hostname 無法解析，因此通常需要明確允許 TCP/UDP 53 到 cluster DNS。
