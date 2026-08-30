# Week18 Day6 — GPU / NIC / NUMA Topology & Locality

## 今日完成內容

今天重點是理解：

- CPU Socket
- NUMA node
- GPU CPU Affinity
- GPU PCIe Bus
- NIC PCIe Bus
- GPU / NIC locality
- 虛擬化環境對實體 topology 可見性的限制

目標是處理這類 HPC / AI Performance 問題：

    GPU workload 可以跑
    但 distributed communication / NCCL scaling 很差

可能原因除了 network bandwidth，也可能包含：

    CPU affinity
    NUMA locality
    GPU / NIC PCIe topology
    cross-NUMA access

---

## 1. Socket 是什麼

CPU Socket 可以理解成：

    一個實體 CPU 插槽 / 一顆實體處理器的位置

例如：

    Motherboard
    ├─ Socket 0
    └─ Socket 1

一個 Socket 裡面可以有很多 CPU core / logical CPU。

所以：

    CPU(s): 4
    Socket(s): 1

不是代表有 4 顆實體 CPU。

而是：

    1 個 Socket
    4 個 OS 可排程 CPU

---

## 2. NUMA 是什麼

NUMA：

    Non-Uniform Memory Access

核心概念：

    CPU 存取靠近自己的 Memory
    → latency 較低

    CPU 存取其他 NUMA domain 的 Memory
    → latency 較高
    → bandwidth 可能較差

NUMA node 可以理解成：

    一個 CPU / Memory locality 區域

例如：

    NUMA node 0
    ├─ CPU 0-15
    └─ Memory A

    NUMA node 1
    ├─ CPU 16-31
    └─ Memory B

因此 HPC 系統會在意：

    CPU
    Memory
    GPU
    NIC

是否位於相近的 locality。

---

## 3. hpc-demo CPU / NUMA

執行：

    lscpu | egrep 'Socket|NUMA|CPU\(s\)'

結果：

    CPU(s): 4
    Socket(s): 1
    NUMA node(s): 1
    NUMA node0 CPU(s): 0-3

代表：

    1 Socket
    1 NUMA node
    CPU 0-3 全部位於 NUMA node0

因此這台環境沒有：

    cross-NUMA memory access

可以實際分析。

---

## 4. GPU Topology Debug Pod

建立暫時 Pod：

    gpu-topology-debug

用途：

    將 debug workload 排到真正的 GKE GPU node
    並取得 GPU node 裡的 topology 資訊

這個 Pod 不跑 training，也不跑 benchmark。

主要只是：

    sleep 3600

讓我們可以：

    kubectl exec

進入 GPU workload environment 執行：

    nvidia-smi
    lspci
    lscpu

---

## 5. GPU Topology

執行：

    nvidia-smi topo -m

結果：

    GPU0
    CPU Affinity: 0-3
    NUMA Affinity: 0
    GPU NUMA ID: N/A

代表：

    GPU0
      ↓
    最接近 CPU 0-3
      ↓
    NUMA node 0

目前只有：

    1 GPU

所以沒有：

    GPU0 ↔ GPU1

可以分析。

---

## 6. CPU Affinity

結果：

    CPU Affinity: 0-3

意思不是：

    GPU 只能使用 CPU 0-3

而是 NVIDIA topology 判斷：

    CPU 0-3
    是跟 GPU0 locality 最接近的一組 CPU

在 HPC / AI workload 中，
CPU thread / data pipeline 如果盡量靠近 GPU，
通常可以降低不必要的 data movement。

---

## 7. NUMA Affinity

結果：

    NUMA Affinity: 0

代表：

    GPU0
    最接近 NUMA node0

目前：

    NUMA node0
    └─ CPU 0-3

所以沒有看到：

    GPU 在 node0
    CPU workload 卻跑到 node1

這類 cross-NUMA 問題。

---

## 8. GPU PCIe Device

執行：

    nvidia-smi \
      --query-gpu=name,pci.bus_id \
      --format=csv,noheader

結果：

    NVIDIA L4, 00000000:00:03.0

所以 GPU：

    NVIDIA L4
    PCIe Bus: 00:03.0

---

## 9. NIC PCIe Device

執行：

    lspci | egrep -i 'NVIDIA|Ethernet|Network'

結果：

    00:03.0  NVIDIA L4
    00:04.0  Virtio network device

所以 VM 中看到：

    GPU
    → PCIe 00:03.0

    NIC
    → PCIe 00:04.0

但這裡不能直接推論：

    GPU 與實體 NIC
    位於同一個 PCIe switch

因為 NIC 是：

    Virtio virtual NIC

不是直接暴露的 physical RDMA NIC。

---

## 10. NIC NUMA Locality

嘗試：

    cat /sys/class/net/eth0/device/numa_node

結果：

    No such file or directory

代表目前 container / VM environment
沒有暴露可以直接判讀的 NIC NUMA locality。

所以：

    GPU NUMA locality
    → 可以看到

    Physical NIC NUMA locality
    → 無法可靠判斷

---

## 11. GPU Node CPU / NUMA

GPU Pod 內：

    lscpu | egrep 'CPU\(s\)|Socket|NUMA'

結果：

    CPU(s): 4
    Socket(s): 1
    NUMA node(s): 1
    NUMA node0 CPU(s): 0-3

因此目前 GPU VM：

    1 Socket
    1 NUMA node
    4 CPU

GPU0 也是：

    NUMA affinity = 0

目前沒有實際 cross-NUMA topology。

---

## 12. 與 NCCL 的關係

如果 production server 有多 NUMA node，
可能出現：

    GPU
      ↓
    NUMA node0
      ↓
    cross-NUMA interconnect
      ↓
    NUMA node1
      ↓
    NIC

這種 data path 可能增加：

    latency

並降低：

    communication bandwidth

因此 NCCL / RDMA troubleshooting 除了看：

    NET/IB
    NET/Socket
    bandwidth
    MTU
    packet loss

也要看：

    GPU ↔ NIC locality
    GPU ↔ CPU affinity
    PCIe topology
    NUMA placement

---

## 13. 本次環境限制

目前 GKE GPU node 是 VM environment。

因此：

    GPU
    → NVIDIA L4
    → PCIe device visible

但 NIC：

    Virtio virtual NIC

虛擬化層會隱藏部分實體 topology。

所以不能從：

    00:03.0 GPU
    00:04.0 NIC

直接判定兩者在實體硬體上一定很接近。

真正 bare-metal HPC server 通常能看到更完整的：

    CPU Socket
    NUMA
    PCIe Host Bridge
    GPU
    NIC
    RDMA device
    NVLink

topology。

---

## 今日結論

今天建立的 topology 判讀方式：

    CPU Socket
      ↓
    NUMA node
      ↓
    CPU Affinity
      ↓
    GPU PCIe
      ↓
    NIC PCIe
      ↓
    GPU / NIC locality

目前實際結果：

    CPU:
    4 CPUs

    Socket:
    1

    NUMA:
    1 node

    GPU:
    NVIDIA L4
    PCIe 00:03.0
    NUMA affinity 0
    CPU affinity 0-3

    NIC:
    Virtio
    PCIe 00:04.0

    Physical NIC NUMA locality:
    not exposed

因此目前沒有觀察到：

    cross-NUMA GPU locality issue

但也無法從 VM 內完整判斷：

    physical GPU ↔ NIC topology

---

## Interview Review

**Q1：為什麼 GPU / NIC NUMA locality 會影響 distributed training？**  
A：如果 GPU 與 NIC 位於不同 NUMA domain，資料可能需要跨 CPU interconnect 傳輸，增加 latency 並降低 effective communication bandwidth。

**Q2：`CPU(s): 4, Socket(s): 1, NUMA node(s): 1` 代表什麼？**  
A：代表 OS 看得到 4 個 CPU 執行單位，但只有 1 個 CPU Socket 與 1 個 NUMA domain，因此目前沒有 cross-NUMA locality 問題。
