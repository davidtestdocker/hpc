<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：網路基礎依本週循序讀；Calico 封包隔離已在隔離叢集驗收，主環境 enforcement 仍關閉。
> **閱讀順序**：先學本文基礎，再讀[Week18 現行對照與檢核](<../../../learning-guide.md#week18>)及[對應現行入口](<../../../runbooks/ai-hpc-job-troubleshooting.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week18 Day7 — End-to-End Distributed Communication Troubleshooting Playbook

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/network/run_iperf3.sh](<../../../../benchmark/network/run_iperf3.sh>)：網路吞吐測試
- [helm/pytorch-runtime/templates/nccl-benchmark-job.yaml](<../../../../helm/pytorch-runtime/templates/nccl-benchmark-job.yaml>)
- [runtime/pytorch/ddp_test.py](<../../../../runtime/pytorch/ddp_test.py>)：CPU／Gloo DDP 實驗

---

## 今日完成內容

今天把 Week18 Day1～Day6 串成一套完整的 AI/HPC distributed communication troubleshooting 流程。

核心目標：

    Distributed training slow
    或
    Pod / node communication failure

不要亂猜原因，而是先判斷：

    不通
    還是
    很慢

再走不同排查路徑。

---

## 1. 第一個判斷：Connectivity vs Performance

### Case A — 完全不通

例如：

    Pod A 無法連到 Pod B
    Service port 無法建立 TCP connection

優先查：

    Kubernetes network path

流程：

    DNS
      ↓
    Service
      ↓
    EndpointSlice
      ↓
    Pod IP
      ↓
    NetworkPolicy
      ↓
    CNI / dataplane

---

### Case B — 可以通，但很慢

例如：

    2-node training 比 single-node 慢很多
    NCCL scaling 很差

優先查：

    Network quality
      ↓
    NCCL transport
      ↓
    RDMA / Socket
      ↓
    NIC performance
      ↓
    GPU / NIC / NUMA locality

---

## 2. Distributed Training Slow

整體排查主幹：

    Distributed training slow
        ↓
    Network baseline
        ↓
    NCCL transport
        ↓
    RDMA availability
        ↓
    GPU / NIC / NUMA topology
        ↓
    Kubernetes network path

不要第一時間只看 GPU utilization。

Distributed workload 同時依賴：

    GPU compute
    NCCL communication
    NIC
    TCP / RDMA
    Kubernetes network
    NUMA / PCIe locality

---

## 3. Network Baseline

如果 workload 一跨 node 就變慢，
先確認底層 network quality。

主要工具：

    ping
    iperf3

檢查：

    RTT
    packet loss
    bandwidth
    TCP Retr
    MTU / PMTU

例如：

    ping -c 20 <peer-ip>

    iperf3 -c <peer-ip> -t 10

如果看到：

    high latency
    packet loss
    high retransmission
    low bandwidth

代表問題已經在底層 network，
不需要先深入 NCCL。

---

## 4. NCCL Transport

如果 network baseline 正常，
下一層查 NCCL。

開啟：

    NCCL_DEBUG=INFO

重點 log：

    NET/IB
    NET/Socket
    Bootstrap
    Using network

---

## 5. NET/IB

NCCL log：

    NET/IB

其中：

    NET
    = Network

    IB
    = InfiniBand backend

NCCL 的 IB backend 用於高效能 RDMA communication，
也可能涵蓋 RoCE 類型的 RDMA transport。

例如：

    NCCL INFO NET/IB : No device found.

代表：

    NCCL 找不到可用的 IB / RDMA device

---

## 6. NET/Socket

如果 RDMA 不可用，
NCCL 可能 fallback：

    NET/Socket

例如本週實際看到：

    NET/IB : No device found
        ↓
    Failed to initialize NET plugin IB
        ↓
    NET/Socket
        ↓
    Using network Socket

代表：

    RDMA unavailable
    → fallback to Socket

Socket path 通常使用一般 TCP/IP network。

---

## 7. RDMA Availability

如果原本預期：

    RDMA / InfiniBand / RoCE

但 NCCL log 卻看到：

    NET/IB : No device found

應檢查：

    RDMA device
    driver
    NCCL network plugin
    NIC capability
    plugin initialization

工具：

    /sys/class/infiniband
    ibv_devinfo

本週實際環境：

    /sys/class/infiniband
    → unavailable

因此：

    RDMA device unavailable

NCCL 最後選擇：

    Socket

---

## 8. Plugin Exists != RDMA Works

本週 image 內：

    NCCL_NET_PLUGIN=spcx

Spectrum-X plugin：

    libnccl-net-spcx.so

成功載入。

但：

    NET/IB : No device found

所以：

    plugin library exists
    !=
    RDMA hardware exists

完整鏈：

    Spectrum-X plugin
        ↓
    plugin loaded
        ↓
    no RDMA device
        ↓
    initialization fails
        ↓
    Socket fallback

---

## 9. GPU / NIC / NUMA Locality

如果：

    network baseline normal
    NCCL transport known

但 communication performance 還是不好，
接著查 hardware locality。

關注：

    CPU
    NUMA
    GPU
    NIC
    PCIe

理想：

    CPU
      ↓
    same NUMA domain
      ↓
    GPU
      ↓
    nearby NIC

較差的情況可能是：

    GPU
      ↓
    NUMA node0
      ↓
    cross-NUMA
      ↓
    NUMA node1
      ↓
    NIC

可能增加：

    latency

降低：

    effective bandwidth

---

## 10. 本次 GPU Topology

實際：

    GPU0
    CPU Affinity: 0-3
    NUMA Affinity: 0

CPU：

    CPU(s): 4
    Socket(s): 1
    NUMA node(s): 1
    NUMA node0 CPU(s): 0-3

因此：

    GPU0
    → NUMA node0

    CPU 0-3
    → NUMA node0

目前沒有：

    cross-NUMA issue

---

## 11. NIC Topology

VM 中：

    GPU:
    NVIDIA L4
    PCIe 00:03.0

    NIC:
    Virtio network device
    PCIe 00:04.0

但 Virtio 是虛擬 NIC。

所以不能直接從：

    00:03.0
    00:04.0

推論真正實體 GPU / NIC PCIe locality。

這是虛擬化環境的重要限制。

---

## 12. Kubernetes Connectivity Path

如果症狀不是慢，
而是：

    Pod 完全連不到

優先查：

    DNS
      ↓
    Service
      ↓
    EndpointSlice
      ↓
    Backend Pod
      ↓
    Pod IP
      ↓
    NetworkPolicy
      ↓
    CNI / dataplane

---

## 13. DNS

檢查：

    nslookup <service>

如果 DNS fail：

    kube-dns
    node-local-dns
    DNS configuration

如果 DNS success：

    代表名稱解析基本正常

但：

    DNS success
    !=
    Service backend success

---

## 14. Service / EndpointSlice

Service 可以存在，
但 backend 可能是空的。

檢查：

    kubectl get svc

    kubectl get endpointslice

如果：

    Service exists
    EndpointSlice empty

代表：

    no backend Pod

優先查：

    selector
    Pod labels
    readiness

---

## 15. Pod IP Direct Test

可以直接：

    nc -vz <pod-ip> <port>

用來繞過 Service abstraction。

判斷：

    Pod IP success
    Service fail
    → Service / EndpointSlice / dataplane

    Pod IP fail
    → backend / NetworkPolicy / CNI / node path

但要先確認：

    Pod IP 是 current backend

避免使用 stale Pod IP。

---

## 16. NetworkPolicy

NetworkPolicy object 存在，
不代表一定有 enforcement。

本週實際：

    NetworkPolicy applied

但 traffic 仍然成功。

GKE：

    networkPolicyConfig:
      disabled: true

所以：

    Policy object exists
    !=
    Policy enforced

需要底層：

    CNI / dataplane

真正支援 enforcement。

---

## 17. CNI / Dataplane

只有在前面：

    DNS OK
    Service OK
    EndpointSlice OK
    Pod backend OK
    NetworkPolicy OK

但 Pod traffic 還是異常時，
才深入查：

    CNI
    Pod routing
    kube-proxy
    iptables
    eBPF dataplane
    node-to-node path

核心原則：

    先縮小 fault domain
    再查底層。

---

## 18. Week18 Full Troubleshooting Tree

### Connectivity Failure

    Pod cannot connect
        ↓
    DNS
        ↓
    Service
        ↓
    EndpointSlice
        ↓
    Pod IP
        ↓
    NetworkPolicy
        ↓
    CNI / dataplane

---

### Performance Failure

    Distributed training slow
        ↓
    ping / iperf3
        ↓
    RTT / loss / Retr / bandwidth
        ↓
    NCCL_DEBUG=INFO
        ↓
    NET/IB or NET/Socket
        ↓
    RDMA availability / fallback
        ↓
    NIC
        ↓
    GPU / NUMA / PCIe locality

---

## 19. Troubleshooting Principle

最重要的原則：

    先判斷症狀
    ↓
    再選 fault domain
    ↓
    用證據排除
    ↓
    不要一開始就猜 CNI / NCCL / GPU

簡化成：

    不通
    → connectivity path

    很慢
    → performance path

---

## 今日結論

Week18 最終建立：

    Linux network diagnostics
    Kubernetes network troubleshooting
    NCCL transport debugging
    RDMA / Socket fallback analysis
    GPU / NIC / NUMA locality analysis

最後整合成：

    Distributed communication troubleshooting playbook

這套方法可以用來分析：

    AI/HPC cluster
    Kubernetes GPU workloads
    distributed training
    NCCL communication
    multi-node performance

而不是只看：

    Pod Running
    GPU utilization

就認為 cluster 沒問題。

---

## Interview Review

**Q1：2-node distributed training 可以正常跑但比 single-node 慢很多，第一步怎麼排查？**  
A：先確認 network baseline，包括 RTT、packet loss、bandwidth、TCP retransmission 與 MTU；底層 network 正常後，再用 `NCCL_DEBUG=INFO` 確認 NCCL transport、RDMA availability 與是否 fallback 到 Socket。

**Q2：Pod 完全連不到另一個 Service，為什麼不應先查 NUMA 或 GPU？**  
A：因為這是 connectivity failure，應先查 DNS、Service、EndpointSlice、Pod IP、NetworkPolicy 與 CNI/dataplane；NUMA/GPU locality 主要影響效能，不是第一優先的連線故障層。
