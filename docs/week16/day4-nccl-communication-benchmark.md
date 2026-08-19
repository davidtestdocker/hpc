# Week16 Day4 — NCCL Communication Benchmark

## 今日成果

平台新增正式 NCCL benchmark Job：

```text
Git
→ ArgoCD
→ Kustomize / Helm
→ Kubernetes Job
→ NVIDIA L4
→ nccl-tests
→ all_reduce_perf
```

本次為真實 Single-GPU benchmark。

---

## Benchmark Command

```bash
./build/all_reduce_perf \
  -b 8K \
  -e 256M \
  -f 2 \
  -g 1
```

參數：

```text
-b 8K
→ 從 8 KB message 開始

-e 256M
→ 最大測到 256 MB

-f 2
→ 每次 message size ×2

-g 1
→ 使用 1 張 GPU
```

---

## 重要輸出欄位

### time

完成一次 AllReduce operation 所需時間。

本次單位：

```text
us = microseconds
```

數值越低代表 operation 越快。

### algBw

Algorithm Bandwidth。

概念上：

```text
資料量 / 執行時間
```

代表 collective operation 的有效 throughput。

### busBw

代表 collective 實際 GPU-to-GPU communication 的 bus bandwidth。

本次：

```text
nranks = 1
busBw = 0
```

因為只有一張 GPU，沒有：

```text
GPU0 ↔ GPU1
```

因此沒有真正 GPU-to-GPU collective communication。

---

## Out-of-place / In-place

### Out-of-place

```text
Input Buffer
↓
AllReduce
↓
另一個 Output Buffer
```

特性：

```text
保留原始 Input
需要額外 Output Buffer
```

### In-place

```text
原本 Buffer
↓
AllReduce
↓
直接覆蓋成結果
```

特性：

```text
省 GPU Memory
原始 Input 被覆蓋
```

判斷原則：

```text
需要保留原資料
→ Out-of-place

原資料之後不用
→ In-place
```

---

## 本次真實結果

NCCL：

```text
rank 0
nranks 1
```

Correctness：

```text
#wrong = 0
Out of bounds values = 0 OK
```

代表 nccl-tests 沒有發現結果錯誤。

Out-of-place 在較大 Message Size 時：

```text
16 MB  ≈ 121.78 GB/s
64 MB  ≈ 115.64 GB/s
128 MB ≈ 115.76 GB/s
256 MB ≈ 115.79 GB/s
```

約在：

```text
115 ~ 122 GB/s
```

附近進入 plateau。

注意：

```text
這不是 GPU-to-GPU NCCL bandwidth。
```

因為本次只有 1 GPU。

---

## 本次可以證明

```text
NCCL Runtime 正常
NCCL Init 成功
nccl-tests Build 成功
all_reduce_perf 執行成功
Message-size benchmark 流程成功
Correctness 驗證成功
Kubernetes NCCL Benchmark Job 成功整合
```

---

## 本次不能證明

```text
Multi-GPU NCCL Bandwidth
NVLink / PCIe GPU-to-GPU Performance
Inter-node NCCL Performance
Socket / RDMA Performance
Multi-GPU Scaling
```

以上需要至少 2 GPU 才能做真實驗證。

---

## Benchmark Artifact

```text
benchmark/results/week16-day4-nccl-single-gpu.txt
```

---

## Quick Review

```text
time
→ 一次 collective 花多久

algBw
→ collective operation throughput

busBw
→ GPU-to-GPU communication bandwidth

1 GPU
→ 沒有 GPU-to-GPU communication
→ busBw = 0

Out-of-place
→ input/output 分開

In-place
→ 結果覆蓋原 buffer
```

---

## Interview Review

### Q1：為什麼單 GPU nccl-tests 的 busBw 是 0？

因為只有一個 rank，沒有 GPU-to-GPU collective communication，因此沒有 bus traffic 可計算。

### Q2：Single-GPU nccl-tests 有什麼價值？

可以驗證 NCCL runtime、benchmark pipeline、correctness、message-size behavior，但不能代表 Multi-GPU communication performance。
