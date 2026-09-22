<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day4 — Kubernetes 網路

[上一課](<day3-packet-level-network-failure-troubleshooting.md>) · [本週目錄](README.md) · [下一課](<day5-nccl-transport-debugging.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史空backend／失效IP／未enforce。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

EndpointSlice是控制面資料，不是封包逐個經過的proxy；未Ready endpoint未必消失，需看conditions。deny與其他allow規則是聯集，不能只見一條deny就斷言應全擋。

## 程式／設定與來源

本次核對：[k8s/api-service.yaml](<../../k8s/api-service.yaml>)、[k8s/security/network-policy/default-deny.yaml](<../../k8s/security/network-policy/default-deny.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<day4-kubernetes-network-troubleshooting.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Endpoints: <none>
```

舊hpc-dev policy不生效，與新隔離Calico驗收是兩個環境；本次不連線重查。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：網路基礎依本週循序讀；Calico 封包隔離已在隔離叢集驗收，主環境 enforcement 仍關閉。
> **閱讀順序**：先學本文基礎，再讀[Week18 現行對照與檢核](../learning-guide.md#week18)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week18 Day4 — Kubernetes Networking Troubleshooting

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

`/tmp/net-debug-deny-egress.yaml` 是實驗時的暫存檔，未保存；下方 NetworkPolicy 檔案是現有相關設定。

- [k8s/api-service.yaml](../../k8s/api-service.yaml)
- [k8s/security/network-policy/allow-dns.yaml](../../k8s/security/network-policy/allow-dns.yaml)
- [k8s/security/network-policy/allow-same-namespace.yaml](../../k8s/security/network-policy/allow-same-namespace.yaml)
- [k8s/security/network-policy/default-deny.yaml](../../k8s/security/network-policy/default-deny.yaml)

---

## 今日完成內容

建立 Kubernetes 網路故障排查流程，從：

- DNS
- Service
- EndpointSlice
- Backend Pod
- Pod IP
- NetworkPolicy
- CNI / dataplane

逐層定位 fault domain。

本次主要 namespace：

    hpc-platform-dev

測試 Pod：

    net-debug

---

## 1. Kubernetes Network Troubleshooting Flow

遇到：

    Pod A 無法連到某個 Service

排查順序：

    DNS
      ↓
    Service
      ↓
    EndpointSlice
      ↓
    Backend Pod
      ↓
    Pod IP direct connection
      ↓
    NetworkPolicy
      ↓
    CNI / dataplane / node path

核心原則：

    不要一看到 Service 連不上，
    就直接假設 CNI 壞掉。

應先逐層縮小 fault domain。

---

## 2. Cluster Network Topology

目前 GKE：

    primary node:
    10.10.0.51

    observability node:
    10.10.0.52

Pod IP 分布主要看到：

    10.68.0.x
    10.68.1.x

代表目前 workload 已存在：

    same-node communication
    cross-node communication

---

## 3. Service 與 Endpoint

查看 Service：

    kubectl get svc -n hpc-platform-dev -o wide

查看舊版 Endpoints：

    kubectl get endpoints -n hpc-platform-dev

新版建議查看：

    kubectl get endpointslices -n hpc-platform-dev

Service：

    提供穩定的 ClusterIP / DNS 名稱

EndpointSlice：

    記錄 Service 背後真正的 Pod IP / port

概念：

    Client Pod
       ↓
    Service ClusterIP
       ↓
    EndpointSlice
       ↓
    Backend Pod

---

## 4. iperf3-server：Service 存在但沒有 Backend

Service：

    iperf3-server
    ClusterIP: 34.118.234.8
    Port: 5201
    Selector: app=iperf3-server

確認 matching Pod：

    kubectl get pods \
      -n hpc-platform-dev \
      -l app=iperf3-server \
      -o wide

結果：

    No resources found

EndpointSlice：

    kubectl get endpointslices \
      -n hpc-platform-dev \
      -l kubernetes.io/service-name=iperf3-server \
      -o wide

結果：

    ENDPOINTS <unset>

describe：

    Endpoints: <none>

所以：

    Service exists
      ↓
    Selector exists
      ↓
    No matching Pod
      ↓
    EndpointSlice empty
      ↓
    No backend

Root cause：

    Service backend / selector layer

不是：

    DNS
    CNI
    Pod-to-Pod routing

---

## 5. DNS 正常，不代表 Service 一定可用

建立 debug Pod：

    kubectl run net-debug \
      -n hpc-platform-dev \
      --image=nicolaka/netshoot \
      --restart=Never \
      -- sleep 3600

進入：

    kubectl exec -it net-debug \
      -n hpc-platform-dev \
      -- bash

測試：

    nslookup iperf3-server

結果：

    iperf3-server.hpc-platform-dev.svc.cluster.local
    Address: 34.118.234.8

完整 FQDN：

    nslookup iperf3-server.hpc-platform-dev.svc.cluster.local

同樣成功解析。

代表：

    Kubernetes DNS 正常
    Service name → ClusterIP 正常

但：

    nc -vz -w 3 iperf3-server 5201

結果：

    Connection refused

原因：

    EndpointSlice 沒有 backend

所以：

    DNS resolve success
    !=
    Service application path success

---

## 6. 正常 Service 對照：Redis

DNS：

    nslookup redis-service

結果：

    redis-service.hpc-platform-dev.svc.cluster.local
    Address: 34.118.235.96

TCP：

    nc -vz -w 3 redis-service 6379

結果：

    succeeded

此時正常鏈路：

    net-debug
      ↓
    redis-service DNS
      ↓
    ClusterIP
      ↓
    EndpointSlice
      ↓
    Redis Pod
      ↓
    TCP 6379 success

---

## 7. NetworkPolicy 測試

先確認：

    kubectl get networkpolicy -n hpc-platform-dev

結果：

    No resources found

替 debug Pod 加 label：

    kubectl label pod net-debug \
      -n hpc-platform-dev \
      role=net-debug

確認：

    kubectl get pod net-debug \
      -n hpc-platform-dev \
      --show-labels

看到：

    role=net-debug

---

## 8. Default Deny Egress Policy

建立：

    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: net-debug-deny-egress
      namespace: hpc-platform-dev
    spec:
      podSelector:
        matchLabels:
          role: net-debug
      policyTypes:
        - Egress
      egress: []

語意：

    選中 role=net-debug 的 Pod
    並 deny 所有 egress traffic

套用：

    kubectl apply -f /tmp/net-debug-deny-egress.yaml

Policy 物件成功建立：

    net-debug-deny-egress

但實測：

    nslookup redis-service
    → success

    nc -vz -w 3 redis-service 6379
    → success

代表：

    NetworkPolicy object exists
    但 dataplane 沒有 enforce

---

## 9. 確認 GKE NetworkPolicy Enforcement

查看 cluster 設定：

    gcloud container clusters describe hpc-dev \
      --zone=asia-east1-a \
      --format='yaml(networkPolicy,datapathProvider,addonsConfig.networkPolicyConfig)'

結果：

    addonsConfig:
      networkPolicyConfig:
        disabled: true

所以 root cause：

    NetworkPolicy enforcement disabled

重要概念：

    kubectl apply NetworkPolicy
      ↓
    Kubernetes API 接受 object
      ↓
    不代表 traffic 一定被限制
      ↓
    CNI / dataplane 必須支援並啟用 enforcement

因此：

    Policy object exists
    !=
    Policy is enforced

---

## 10. Cleanup NetworkPolicy

刪除：

    kubectl delete networkpolicy \
      net-debug-deny-egress \
      -n hpc-platform-dev

確認：

    kubectl get networkpolicy \
      -n hpc-platform-dev

結果：

    No resources found

---

## 11. Pod IP Direct Connection

Service troubleshooting 時，
可以繞過 Service，直接測 backend Pod IP：

    nc -vz -w 3 <pod-ip> <port>

用途：

    判斷問題是在 Service abstraction
    還是 backend Pod / Pod network path

---

## 12. Old Pod IP Case

原本記錄的 Redis Pod IP：

    10.68.0.16

測試：

    nc -vz -w 3 10.68.0.16 6379

結果：

    Connection refused

但：

    nc -vz -w 3 redis-service 6379

仍然：

    succeeded

一開始看起來像：

    Pod IP fail
    Service success

但不能直接判斷 CNI 問題。

---

## 13. 確認 Redis 最新 Pod IP

查看：

    kubectl get pod \
      -n hpc-platform-dev \
      -l app=redis \
      -o wide

結果：

    redis-5894bb54d-qsm2k
    IP: 10.68.0.21

所以：

    10.68.0.16

已經是舊 Pod IP。

測試新 IP：

    nc -vz -w 3 10.68.0.21 6379

結果：

    succeeded

因此：

    old Pod IP
    → fail

    current Pod IP
    → success

    Service
    → success

---

## 14. Pod IP 與 Service 的差別

Pod IP：

    不是穩定 identity

Pod 被：

    recreated
    rescheduled
    replaced

都可能取得新的 Pod IP。

Service：

    提供穩定 ClusterIP / DNS
    並由 EndpointSlice 指向目前正確 backend

所以：

    Application
    不應長期依賴某個固定 Pod IP

應使用：

    Service DNS
    或
    Service ClusterIP

---

## 15. Pod IP vs Service Troubleshooting

如果：

    Pod IP success
    Service fail

優先查：

    Service selector
    EndpointSlice
    port
    targetPort
    kube-proxy / dataplane

如果：

    Pod IP fail
    Service fail

優先查：

    Pod listener
    Pod readiness
    NetworkPolicy
    CNI
    node network path

但在測 Pod IP 前一定先確認：

    Pod IP 是否仍然是 current backend

避免拿 stale Pod IP 做錯誤判斷。

---

## 16. CNI / Dataplane

CNI：

    Container Network Interface

負責 Kubernetes Pod networking 的基礎能力。

當：

    DNS OK
    Service OK
    EndpointSlice OK
    Backend Pod Ready
    NetworkPolicy 正常

但 Pod IP 仍無法互通時，
才應進一步查：

    Pod routing
    node-to-node path
    CNI agent
    kube-proxy
    iptables / eBPF dataplane
    node NIC / route

核心原則：

    先縮小 fault domain
    再進入 CNI deep troubleshooting

---

## 17. 今日三個故障案例

### Case 1 — Service 沒 Backend

    DNS: OK
    Service: exists
    EndpointSlice: empty
    Pod: none

Root cause：

    backend / selector layer

---

### Case 2 — NetworkPolicy 不生效

    NetworkPolicy object: exists
    Pod selector: match
    Traffic: still success

Cluster config：

    networkPolicyConfig.disabled: true

Root cause：

    policy enforcement disabled

---

### Case 3 — Pod IP 失效

    old Pod IP:
    10.68.0.16
    → fail

    current Pod IP:
    10.68.0.21
    → success

    redis-service:
    → success

Root cause：

    stale Pod IP

不是：

    CNI failure

---

## 18. Production Troubleshooting Playbook

遇到：

    Pod cannot reach Service

依序檢查：

    1. DNS

       nslookup <service>

       ↓

    2. Service

       kubectl get svc
       kubectl describe svc

       ↓

    3. EndpointSlice

       kubectl get endpointslice

       ↓

    4. Backend Pod

       kubectl get pod -o wide

       ↓

    5. Pod IP direct test

       nc / curl

       ↓

    6. NetworkPolicy

       kubectl get networkpolicy

       ↓

    7. Cluster enforcement

       CNI / dataplane config

       ↓

    8. Node / CNI path

       route
       kube-proxy
       dataplane
       node networking

---

## 今日結論

Day4 將 Linux network troubleshooting 延伸到 Kubernetes。

核心不是看到連線失敗就猜 CNI，
而是建立證據鏈：

    DNS
      ↓
    Service
      ↓
    EndpointSlice
      ↓
    Pod
      ↓
    NetworkPolicy
      ↓
    CNI / dataplane

本次實際驗證：

    Service can exist without backend
    DNS can work while Service traffic fails
    NetworkPolicy object can exist without enforcement
    Pod IP can change after Pod replacement
    Service remains stable across Pod replacement

---

## Interview Review

**Q1：Kubernetes Service 可以存在但完全無法提供流量嗎？為什麼？**  
A：可以。Service 物件與 ClusterIP 可以存在，但如果 selector 沒有匹配到 Ready backend Pod，EndpointSlice 會是空的，因此沒有實際 backend 可以接流量。

**Q2：NetworkPolicy 已經成功 apply，但 traffic 還是可以通，應該查什麼？**  
A：除了確認 podSelector 與 policy rule，也要確認叢集 CNI / dataplane 是否支援並啟用 NetworkPolicy enforcement。Policy object 存在不代表 dataplane 一定有執行。
