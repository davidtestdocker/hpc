<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day4 — NCCL benchmark 邊界

[上一課](<day3-nccl-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day5-distributed-training-scaling.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

all-reduce benchmark 需交代 rank 數、訊息大小、裝置與鏈路；單 rank 數字不能當 inter-node bandwidth。algbw 與 busbw 也有不同定義，不能混報。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[benchmark/results/week16-day4-nccl-single-gpu.txt](<../../benchmark/results/week16-day4-nccl-single-gpu.txt>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
=== Clone nccl-tests ===
Cloning into '/opt/nccl-tests'...
=== Build nccl-tests ===
make -C src build BUILDDIR=/opt/nccl-tests/build
make[1]: Entering directory '/opt/nccl-tests/src'
make[2]: Entering directory '/opt/nccl-tests/os'
Compiling  timer.cc                            > /opt/nccl-tests/build/timer.o
Compiling /opt/nccl-tests/build/verifiable/verifiable.o
Compiling  all_reduce.cu                       > /opt/nccl-tests/build/all_reduce.o
Compiling  linux.cc                            > /opt/nccl-tests/build/os/linux.o
Compiling  common.cu                           > /opt/nccl-tests/build/common.o
Creating archive /opt/nccl-tests/build/os/linux.o    > /opt/nccl-tests/build/os/libnccl_test_os.a
make[2]: Leaving directory '/opt/nccl-tests/os'
Compiling  util.cu                             > /opt/nccl-tests/build/util.o
Compiling  all_gather.cu                       > /opt/nccl-tests/build/all_gather.o
Compiling  broadcast.cu                        > /opt/nccl-tests/build/broadcast.o
Compiling  reduce_scatter.cu                   > /opt/nccl-tests/build/reduce_scatter.o
Compiling  reduce.cu                           > /opt/nccl-tests/build/reduce.o
Compiling  alltoall.cu                         > /opt/nccl-tests/build/alltoall.o
Compiling  alltoallv.cu                        > /opt/nccl-tests/build/alltoallv.o
Compiling  scatter.cu                          > /opt/nccl-tests/build/scatter.o
Compiling  gather.cu                           > /opt/nccl-tests/build/gather.o
Compiling  sendrecv.cu                         > /opt/nccl-tests/build/sendrecv.o
Compiling  hypercube.cu                        > /opt/nccl-tests/build/hypercube.o
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week16/day4-nccl-communication-benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：CPU／Gloo DDP、單 rank NCCL 與新單 L4 訓練是不同證據，未驗證多 GPU／RDMA scaling。
> **閱讀順序**：先學本文基礎，再讀[Week16 現行對照與檢核](../learning-guide.md#week16)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week16 Day4 — NCCL Communication Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/results/week16-day4-nccl-single-gpu.txt](../../benchmark/results/week16-day4-nccl-single-gpu.txt)：單 GPU NCCL 原始結果
- [helm/pytorch-runtime/templates/nccl-benchmark-job.yaml](../../helm/pytorch-runtime/templates/nccl-benchmark-job.yaml)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)

---

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
