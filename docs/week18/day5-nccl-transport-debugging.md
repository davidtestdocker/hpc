<!-- readable-curriculum: 2026-09-22 -->
# Week18 Day5 — NCCL transport 排障

[上一課](<day4-kubernetes-network-troubleshooting.md>) · [本週目錄](README.md) · [下一課](<day6-gpu-nic-numa-topology.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

找不到 IB 裝置後選 Socket 可能是正常 fallback。要判斷通訊成功須看 ranks、初始化及實際 collective，不是只截一行 WARN。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[docs/demo/nccl-transport-fallback-demo.md](<../demo/nccl-transport-fallback-demo.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
從保存的 NCCL raw log 說明 transport discovery、IB 初始化失敗與 Socket fallback 的判讀。來源為 [原始單 GPU log](../../benchmark/results/week16-day4-nccl-single-gpu.txt) 與 [transport 排障紀錄](../history/20260922-before-current/week18/day5-nccl-transport-debugging.md)；本輪未執行 NCCL test。

## NCCL Transport Discovery

歷史環境為 **1 GPU（NVIDIA L4）、1 rank、1 node，沒有 RDMA hardware**。紀錄中的 `NCCL_NET_PLUGIN=spcx` 使 NCCL 嘗試載入 Spectrum-X plugin；plugin library 可載入，但底層沒有可用 IB／RDMA device。

面試展示時先開 raw log，依序查看 plugin discovery、NET/IB、NET/Socket、communicator initialization，再確認 rank／node 數量。這些輸出描述 backend selection，不能單憑它們判斷跨機傳輸效能。

## Observed Log

以下逐行摘自 raw log，省略其他中間行，沒有改寫訊息：

```text
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/Plugin: Loaded net plugin SPCX (v12)
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/IB : No device found.
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Failed to initialize NET plugin SPCX
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Failed to initialize NET plugin IB
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/Socket : Using [0]eth0:10.56.0.6<0>
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Initialized NET plugin Socket
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Assigned NET plugin Socket to comm
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Using network Socket
nccl-benchmark-csgjr:1:1 [0] NCCL INFO comm 0x59e6b47a3b40 rank 0 nRanks 1 nNodes 1 localRanks 1 localRank 0 MNNVL 0
nccl-benchmark-csgjr:1:1 [0] NCCL INFO ncclCommInitRankConfig comm 0x59e6b47a3b40 rank 0 nranks 1 cudaDev 0 nvmlDev 0 busId 30 commId 0xa3c39faff10c2201 - Init COMPLETE
```
````

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week18/day5-nccl-transport-debugging.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：網路基礎依本週循序讀；Calico 封包隔離已在隔離叢集驗收，主環境 enforcement 仍關閉。
> **閱讀順序**：先學本文基礎，再讀[Week18 現行對照與檢核](../learning-guide.md#week18)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week18 Day5 — NCCL Transport Debugging：Socket / RDMA Fallback

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

`/tmp/all.yaml`、`/tmp/nccl-benchmark.yaml` 是渲染產物；請從下方 Helm 模板與 values 查看來源。

- [benchmark/results/week16-day4-nccl-single-gpu.txt](../../benchmark/results/week16-day4-nccl-single-gpu.txt)：單 GPU NCCL 原始結果
- [helm/pytorch-runtime/templates/nccl-benchmark-job.yaml](../../helm/pytorch-runtime/templates/nccl-benchmark-job.yaml)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)

---

## 今日完成內容

建立 NCCL distributed communication 的 transport troubleshooting 流程，實際驗證：

- NCCL network plugin 偵測
- Spectrum-X plugin 載入
- IB / RDMA device availability
- RDMA 初始化失敗
- Socket fallback
- NCCL 使用的 network interface
- GKE GPU node taint 對 system Pod / log access 的影響

本次環境：

    GKE GPU Cluster: hpc-gpu-sg
    Node Pool: gpu-pool
    GPU: 1 × NVIDIA L4
    NCCL: 2.30.7
    CUDA Driver: 13.3
    Container: nvcr.io/nvidia/pytorch:26.07-py3

---

## 1. NCCL Transport Troubleshooting Flow

遇到 distributed training communication 效能異常時：

    NCCL_DEBUG=INFO
        ↓
    NCCL 選哪個 NIC？
        ↓
    NET/IB 還是 NET/Socket？
        ↓
    RDMA device 是否存在？
        ↓
    Network plugin 是否初始化成功？
        ↓
    是否 fallback 到 Socket？
        ↓
    bandwidth / latency / loss / MTU

不要直接假設：

    NCCL 慢
    =
    GPU 問題

也可能是：

    NIC selection
    RDMA unavailable
    transport fallback
    TCP network bottleneck

---

## 2. Host RDMA Capability Check

在 hpc-demo 檢查：

    ls -l /sys/class/infiniband

結果：

    No such file or directory

代表目前 host 沒有可用 InfiniBand / RDMA device。

雖然：

    which ibv_devinfo

結果存在：

    /usr/bin/ibv_devinfo

但：

    RDMA tool exists
    !=
    RDMA hardware exists

目前 NIC：

    lo
    ens4
    docker0

沒有 InfiniBand device。

---

## 3. Existing NCCL Benchmark Job

沿用 Week16 的 NCCL benchmark：

    helm/pytorch-runtime/templates/nccl-benchmark-job.yaml

主要設定：

    NCCL_DEBUG=INFO

    nvidia.com/gpu: 1

    gpusPerProcess: 1

Benchmark：

    ./build/all_reduce_perf \
      -b 8K \
      -e 256M \
      -f 2 \
      -g 1

本次只有：

    1 GPU
    1 rank
    1 node

因此主要用途是：

    NCCL init
    network detection
    transport selection

不能視為真正的 multi-node NCCL benchmark。

---

## 4. Helm Resource Collision

直接執行：

    helm upgrade --install pytorch-runtime ...

失敗：

    Deployment "pytorch-runtime" exists
    cannot be imported into current release
    invalid ownership metadata

原因：

    既有 pytorch-runtime Deployment
    不是目前 Helm release 建立

因此沒有強制接管既有 resource。

改成：

    Helm chart
        ↓
    helm template
        ↓
    render ordinary Kubernetes YAML
        ↓
    only extract nccl-benchmark Job
        ↓
    kubectl apply

避免修改其他既有平台 workload。

---

## 5. NCCL Debug Job

從 Helm render：

    helm template pytorch-runtime \
      ./helm/pytorch-runtime \
      -n hpc-platform-dev \
      > /tmp/all.yaml

只抽出：

    kind: Job
    metadata.name: nccl-benchmark

建立：

    /tmp/nccl-benchmark.yaml

Day5 Job 改名：

    nccl-transport-debug

避免跟既有 Week16 benchmark 衝突。

---

## 6. Namespace Mistake

第一次：

    kubectl apply -f /tmp/nccl-benchmark.yaml

因 manifest 沒有：

    metadata.namespace

而 kubectl 也沒有：

    -n hpc-platform-dev

所以 Job 被建立到：

    default

而不是：

    hpc-platform-dev

確認：

    default/nccl-benchmark
    → Running

    hpc-platform-dev/nccl-benchmark
    → old Complete job

處理方式：

    delete wrong default job

並重新建立：

    hpc-platform-dev/nccl-transport-debug

---

## 7. GPU Scheduling Failure

新 Pod 最初：

    Pending

Event：

    0/1 nodes are available:
    1 Insufficient nvidia.com/gpu

原因：

    Cluster 只有 1 張 GPU

    default/nccl-benchmark
    → Terminating
    → still requests 1 GPU

    nccl-transport-debug
    → requests another 1 GPU

所以：

    GPU capacity = 1
    allocated = 1
    new request = 1
    → Pending

舊 Pod 清除後：

    nccl-transport-debug
    → Running

---

## 8. kubectl logs Failure

第一次抓 log：

    kubectl logs ...

結果：

    No agent available

目標：

    https://10.148.0.19:10250/containerLogs/...

但 NCCL Pod 本身：

    Running
    Ready=True
    GPU allocated
    Container Started

所以不是 NCCL failure。

---

## 9. Konnectivity Agent Root Cause

Cluster 中：

    konnectivity-agent
    → Pending

Event：

    0/1 nodes are available:
    1 node(s) had untolerated taint(s)

GPU node taint：

    nvidia.com/gpu=present:NoSchedule

Cluster 當時只有這一台 GPU node。

因此：

    GPU node has NoSchedule taint
        ↓
    konnectivity-agent has no matching toleration
        ↓
    agent cannot schedule
        ↓
    control plane cannot reach kubelet log endpoint
        ↓
    kubectl logs
        ↓
    No agent available

移除 taint：

    kubectl taint node \
      gke-hpc-gpu-sg-gpu-pool-9ad99345-tkqb \
      nvidia.com/gpu=present:NoSchedule-

之後 log access 恢復。

---

## 10. NCCL Network Detection Result

關鍵 log：

    NCCL INFO Bootstrap: Using eth0:10.56.0.6<0>

    NCCL INFO NET/IB : No device found.

    NCCL INFO Failed to initialize NET plugin SPCX

    NCCL INFO Failed to initialize NET plugin IB

    NCCL INFO NET/Socket : Using [0]eth0:10.56.0.6<0>

    NCCL INFO Initialized NET plugin Socket

    NCCL INFO Assigned NET plugin Socket to comm

    NCCL INFO Using network Socket

實際 transport selection：

    NCCL
      ↓
    Spectrum-X plugin detected
      ↓
    IB / RDMA device check
      ↓
    No device found
      ↓
    SPCX initialization failed
      ↓
    IB initialization failed
      ↓
    fallback to Socket
      ↓
    eth0:10.56.0.6

---

## 11. Spectrum-X Plugin

Container 預設 environment：

    NCCL_NET_PLUGIN=spcx
    NCCL_VERSION=2.30.7

Spectrum-X plugin：

    /opt/hpcx/nccl_spectrum-x_plugin/lib/libnccl-net-spcx.so

Log 顯示：

    Successfully loaded external network plugin

但之後：

    NET/IB : No device found

所以：

    plugin library exists
    !=
    RDMA hardware exists

NCCL 能載入 plugin，
不代表底層 NIC 具備 RDMA capability。

---

## 12. Socket Fallback

因為 RDMA path 不可用，NCCL 最後：

    NET/Socket

使用：

    eth0
    10.56.0.6

最後：

    Using network Socket

這代表 NCCL network backend 已選擇 Socket。

---

## 13. NCCL Init Result

Log：

    NCCL version 2.30.7+cuda13.3

    rank 0
    nranks 1

    nNodes 1
    localRanks 1

    ncclCommInitRankConfig
    Init COMPLETE

代表：

    NCCL runtime OK
    CUDA/NCCL init OK
    network plugin discovery OK
    Socket plugin init OK
    communicator init OK

---

## 14. Environment Limitation

本次：

    nranks = 1
    nNodes = 1
    GPU = 1

因此可以證明：

    NCCL network detection works
    IB/RDMA unavailable
    Spectrum-X plugin attempted
    Socket selected
    eth0 selected
    NCCL communicator initialized

但不能證明：

    real inter-node NCCL traffic
    real RDMA bandwidth
    TCP vs RDMA performance comparison
    multi-node AllReduce bandwidth
    NCCL scaling efficiency

這些需要至少：

    2 ranks
    preferably 2 nodes
    RDMA-capable NICs for real RDMA validation

---

## 15. Production NCCL Troubleshooting Playbook

遇到：

    distributed training slow

先開：

    NCCL_DEBUG=INFO

看：

    NET/IB
    NET/Socket
    Bootstrap
    NIC name
    plugin initialization

判斷：

    NET/IB success
    → RDMA path available

    NET/IB No device found
    + NET/Socket success
    → RDMA unavailable, Socket fallback

再往下查：

    NIC bandwidth
    RTT
    packet loss
    TCP retransmission
    MTU / PMTU
    route
    NIC counters
    GPU / NIC NUMA locality

---

## 今日結論

Day5 將 Linux network troubleshooting 接到 NCCL distributed communication。

本次實際 transport detection：

    NCCL_NET_PLUGIN=spcx
        ↓
    Spectrum-X plugin loaded
        ↓
    NET/IB : No device found
        ↓
    IB / RDMA unavailable
        ↓
    NET/Socket initialized
        ↓
    eth0:10.56.0.6
        ↓
    Using network Socket

另外也定位：

    GPU node NoSchedule taint
        ↓
    konnectivity-agent Pending
        ↓
    kubectl logs No agent available

證明 HPC / AI cluster troubleshooting 不只要看 GPU，
還要同時理解：

    Kubernetes scheduling
    cluster networking
    NCCL transport
    NIC / RDMA capability

---

## Interview Review

**Q1：NCCL log 出現 `NET/IB : No device found`，但最後 `Using network Socket`，代表什麼？**  
A：代表 NCCL 無法找到可用的 IB/RDMA device，因此 RDMA transport 初始化失敗，最後 fallback 到 Socket network backend。

**Q2：NCCL plugin library 成功載入，是否代表 RDMA 一定可用？**  
A：不代表。Plugin 只是軟體層，仍需要底層 RDMA-capable NIC、driver 與 device 正常存在；本次 Spectrum-X plugin 成功載入，但因沒有 IB/RDMA device，最後仍改走 Socket。
