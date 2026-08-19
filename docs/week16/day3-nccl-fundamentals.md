# Week16 Day3 — NCCL Fundamentals

## 今日重點

NCCL（NVIDIA Collective Communications Library）是 NVIDIA 的 GPU collective communication library。

PyTorch DDP 在 GPU 環境中，常透過 NCCL 做多 GPU gradient synchronization。

---

## 1. 常見 Collective

### AllReduce

每個 Rank 都有資料，做 Reduce 後，每個 Rank 都拿到完整結果。

```text
Rank0: 1
Rank1: 3

AllReduce SUM

Rank0: 4
Rank1: 4
```

DDP 最重要的用途：

```text
Gradient Synchronization
```

### AllGather

每個 Rank 把自己的資料分享給所有 Rank。

```text
Rank0: A
Rank1: B

→

Rank0: A,B
Rank1: A,B
```

### ReduceScatter

先 Reduce，再把結果切開分給不同 Rank。

### Broadcast

由一個 Rank 把資料傳給所有其他 Rank。

---

## 2. nccl-tests

`nccl-tests` 是測試 NCCL correctness 與 communication performance 的常用工具。

最重要：

```bash
all_reduce_perf
```

常見參數：

```text
-b = 起始 message size
-e = 最大 message size
-f = 每次 message size 放大倍率
-g = 每個 process 使用的 GPU 數
```

範例：

```bash
./build/all_reduce_perf \
  -b 8K \
  -e 256M \
  -f 2 \
  -g 2
```

代表：

```text
從 8 KB 開始
每次放大 2 倍
測到 256 MB
使用 2 GPU
```

---

## 3. Small Message / Large Message

Message size 就是這次 collective 要傳輸的資料量。

### Small Message

例如：

```text
8 KB
32 KB
```

固定 communication overhead 佔比較高。

主要觀察：

```text
Latency
```

### Large Message

例如：

```text
64 MB
256 MB
```

資料搬運成本佔比較高。

主要觀察：

```text
Bandwidth
```

通常：

```text
Message Size ↑
→ Bandwidth ↑
→ 最後進入 Plateau
```

Plateau 代表 communication bandwidth 已逐漸接近上限。

---

## 4. algBw / busBw

### algBw

Algorithm Bandwidth。

代表：

```text
從 Collective Operation 的角度
看這次資料處理得有多快
```

可理解成：

```text
應用 / Collective 視角
```

### busBw

Bus Bandwidth。

代表：

```text
把 Collective 實際 communication pattern 考慮進去後
換算底層 communication fabric 的 bandwidth
```

可理解成：

```text
底層 Interconnect 視角
```

簡化記法：

```text
algBw
→ Collective 有多快

busBw
→ 底層 Communication Path 跑得多快
```

---

## 5. NCCL Debug

開啟 NCCL INFO log：

```bash
export NCCL_DEBUG=INFO
```

主要用來看：

```text
NCCL 是否初始化成功
Rank 是否成功連線
選了哪張 NIC
使用什麼 Transport
```

更詳細：

```bash
export NCCL_DEBUG=TRACE
```

一般 troubleshooting 先用 `INFO`。

---

## 6. NCCL_SOCKET_IFNAME

指定 NCCL 使用哪張 Network Interface：

```bash
export NCCL_SOCKET_IFNAME=eth0
```

例如主機可能有：

```text
eth0
eth1
docker0
cni0
lo
```

如果 NCCL 選錯 NIC，可能造成：

```text
Multi-node communication 失敗
或
Bandwidth 很差
```

---

## 7. NCCL Transport

### Intra-node

同一台機器 GPU 之間：

```text
GPU
↕
PCIe / NVLink
↕
GPU
```

### Inter-node

跨不同 Node：

```text
GPU
↓
PCIe
↓
NIC
↓
Socket / RDMA
↓
NIC
↓
PCIe
↓
GPU
```

NCCL 是 communication library。

底層真正搬資料的可能是：

```text
PCIe
NVLink
Socket
RDMA
```

---

## 8. Troubleshooting Flow

遇到：

```text
DDP 很慢
Multi-GPU Scaling 很差
```

先：

```text
nccl-tests
↓
看 time / algBw / busBw
↓
比較 Small / Large Message
↓
比較 Single-node / Multi-node
↓
NCCL_DEBUG=INFO
↓
確認 NIC / Transport / Rank
↓
必要時調整 NCCL_SOCKET_IFNAME
↓
重新 Benchmark
```

如果：

```text
Single-node 快
Multi-node 很慢
```

優先懷疑：

```text
NIC
Network
Socket / RDMA
NCCL Interface Selection
Inter-node Topology
```

---

## 9. 本日環境限制

目前環境確認：

```text
PyTorch: 2.12.0+cu126
CUDA Runtime: 12.6
NCCL: 2.29.3
NCCL available: True
```

目前只有 1 張 NVIDIA L4。

因此：

```text
尚未取得真實 Multi-GPU NCCL Benchmark 數據
```

模擬數據只能拿來學習判讀，不可當成真實測量結果。

---

## Quick Review

```text
NCCL
→ GPU Collective Communication

AllReduce
→ DDP Gradient Synchronization 最重要

Small Message
→ Latency / Fixed Overhead

Large Message
→ Bandwidth

algBw
→ Collective 視角

busBw
→ Communication Fabric 視角

NCCL_DEBUG=INFO
→ 查 NCCL 通訊決策

NCCL_SOCKET_IFNAME
→ 指定 Network Interface
```

---

## Interview Review

### Q1：為什麼 nccl-tests 要測不同 Message Size？

小 Message 主要反映 latency 與固定 communication overhead；大 Message 主要反映 bandwidth 能力。

### Q2：如果 Single-node NCCL 正常，但 Multi-node 很慢，你會先查什麼？

先查 NCCL_DEBUG log、NIC 選擇、Network、Transport 與 Inter-node communication path。
