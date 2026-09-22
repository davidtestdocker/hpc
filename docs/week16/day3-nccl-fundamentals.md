<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day3 — NCCL collective

[上一課](<day2-pytorch-ddp.md>) · [本週目錄](README.md) · [下一課](<day4-nccl-communication-benchmark.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：NCCL概念與單rank版本log。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

busBw是按collective模型換算的指標，不是NIC實測counter；本課PyTorch環境2.29.3與後日NGC2.30.7不是同版本。不可把NET/Socket初始化當成跨節點傳輸驗證。

## 程式／設定與來源

本次核對：[helm/pytorch-runtime/templates/nccl-benchmark-job.yaml](<../../helm/pytorch-runtime/templates/nccl-benchmark-job.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<../../benchmark/results/week16-day4-nccl-single-gpu.txt>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
NCCL version 2.30.7+cuda13.3
```

既有raw標明2.30.7、單L4，與文字的舊框架版本分開。

**仍缺的證據／不能證明的事：** 單 rank raw log 已保存；缺精確執行日期與完整部署快照，也沒有多 GPU／跨節點通訊結果。本輪未重跑。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：CPU／Gloo DDP、單 rank NCCL 與新單 L4 訓練是不同證據，未驗證多 GPU／RDMA scaling。
> **閱讀順序**：先學本文基礎，再讀[Week16 現行對照與檢核](../learning-guide.md#week16)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week16 Day3 — NCCL Fundamentals

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

下方 NCCL 原始結果為單 GPU／單 rank 紀錄，供對照概念，並非多 GPU 效能證據。

- [benchmark/results/week16-day4-nccl-single-gpu.txt](../../benchmark/results/week16-day4-nccl-single-gpu.txt)：單 GPU NCCL 原始結果
- [helm/pytorch-runtime/templates/nccl-benchmark-job.yaml](../../helm/pytorch-runtime/templates/nccl-benchmark-job.yaml)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)

---

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
