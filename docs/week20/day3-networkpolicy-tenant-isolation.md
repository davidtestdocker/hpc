# Week20 Day3 — NetworkPolicy / Tenant Isolation

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

## 10. Current GKE Limitation

目前 hpc-gpu-sg：

    addonsConfig:
      networkPolicyConfig:
        disabled: true

代表目前 GKE 沒有啟用 NetworkPolicy enforcement。

因此本次完成：

    NetworkPolicy design             ✅
    Kubernetes API schema validation ✅
    Declarative manifests            ✅

未宣稱完成：

    Actual packet deny validation    ❌

啟用 GKE NetworkPolicy 需要調整 cluster networking，
且會造成 node rolling update。

目前單 GPU node lab 不為此額外重建 cluster。

---

## Interview Review

**Q1：Kubernetes Namespace 是否會自動隔離不同 namespace 的 Pod 網路？**  
A：不會。Namespace 主要是邏輯與資源管理邊界；Pod 網路隔離需要支援 NetworkPolicy enforcement 的 CNI，再透過 default deny 與 explicit allow 建立 traffic policy。

**Q2：Default Deny 後為什麼通常要另外允許 DNS？**  
A：因為 Egress Default Deny 也會阻止 Pod 對 DNS server 的流量，造成 Service hostname 無法解析，因此通常需要明確允許 TCP/UDP 53 到 cluster DNS。
