<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-2 — Storage benchmark 子章

[上一課](<day7-1-cpu-benchmark.md>) · [本週目錄](README.md) · [下一課](<day7-3-network-benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

同一磁碟在不同 bs、rw、iodepth 和 direct 模式下是不同 workload。throughput 常與 IOPS 乘以區塊大小相關，但需注意單位與實際完成量。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[benchmark/storage/run_fio.sh](<../../benchmark/storage/run_fio.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
# 效能測試腳本（run_fio）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

SIZE=${1:-1G}
RUNTIME=${2:-60}

echo "================================"
echo " Storage Benchmark"
echo "================================"

echo "Test Size: ${SIZE}"
echo "Runtime: ${RUNTIME}s"

echo ""

# 儲存壓測：size 設定檔案大小、rw 指定讀寫模式、bs 設定區塊大小、direct 避開頁面快取。
fio \
  --name=storage-test \
  --filename=/tmp/fio-test-file \
  --size=${SIZE} \
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-2-storage-benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-2 - Storage Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口
- [benchmark/storage/results/fio_20260810.md](../../benchmark/storage/results/fio_20260810.md)
- [benchmark/storage/run_fio.sh](../../benchmark/storage/run_fio.sh)：儲存 I/O 壓測

---

## 今天平台增加了什麼？

本次加入 Storage I/O Benchmark Module。

使用 fio 建立可控制的 Storage workload，
量測 Kubernetes Node 上 Container Filesystem 的：

- Bandwidth
- IOPS
- Latency

目前 Benchmark Framework 已具備：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Redis Benchmark
- HTTP Benchmark


---

# Architecture

```text
GKE Cluster

primary-pool Node VM
        |
        |
 benchmark Pod
        |
        |
      fio
        |
        |
/tmp/fio-test-file
        |
        |
Container Filesystem
        |
        |
Node Ephemeral Storage
```

本次測試的是：

```text
Container Filesystem / Node Ephemeral Storage
```

不是：

```text
PostgreSQL PVC
```

因此本次結果主要代表目前 GKE Node 上 Container Storage 的 I/O 表現。


---

# Tool

使用：

```text
fio
```

全名：

```text
Flexible I/O Tester
```

版本：

```text
fio-3.33
```

fio 是常用的 Storage Benchmark Tool。

可以模擬：

- Sequential Read
- Sequential Write
- Random Read
- Random Write
- Mixed Read / Write

並觀察：

- Bandwidth
- IOPS
- Latency


---

# 為什麼 HPC / AI 需要 Storage Benchmark？

AI workload 不只有 CPU / GPU。

典型流程：

```text
Dataset

   ↓

Storage

   ↓

CPU preprocessing

   ↓

GPU Training
```

如果 Storage 太慢：

```text
GPU 等待資料

↓

GPU Utilization 降低

↓

Training Time 增加
```

因此 HPC / AI Performance Engineer 需要分析：

- Dataset Loading Speed
- Checkpoint Write Speed
- Storage Throughput
- Storage IOPS
- Storage Latency


---

# Benchmark Script

位置：

```text
benchmark/storage/run_fio.sh
```

內容：

```bash
#!/bin/bash

set -e

SIZE=${1:-1G}
RUNTIME=${2:-60}

echo "================================"
echo " Storage Benchmark"
echo "================================"

echo "Test Size: ${SIZE}"
echo "Runtime: ${RUNTIME}s"

echo ""

fio \
  --name=storage-test \
  --filename=/tmp/fio-test-file \
  --size=${SIZE} \
  --rw=readwrite \
  --bs=4k \
  --direct=1 \
  --runtime=${RUNTIME} \
  --time_based \
  --group_reporting
```

執行：

```bash
./run_fio.sh 1G 60
```

代表：

```text
Test Size:
1GB

Runtime:
60 seconds
```


---

# Benchmark Parameters

## --name

```bash
--name=storage-test
```

設定 fio Job 名稱。


---

## --filename

```bash
--filename=/tmp/fio-test-file
```

指定測試檔案位置。

本次：

```text
/tmp
```

位於 benchmark Pod 的 Container Filesystem。


---

## --size

```bash
--size=1G
```

建立約：

```text
1GB
```

的測試資料範圍。

這不是代表只傳輸 1GB 就結束。

而是 fio 會對這個 1GB Working Set 持續進行 I/O。


---

## --rw

```bash
--rw=readwrite
```

代表 Mixed Read / Write workload。

fio 會同時進行：

```text
Read
+
Write
```

模擬一般 Storage I/O workload。


---

## --bs

```bash
--bs=4k
```

每次 I/O 操作大小：

```text
4KB
```

小 Block Size 比較著重：

```text
IOPS
+
Latency
```

常用於：

- Database
- Small-file workload
- Random I/O analysis


---

## --direct

```bash
--direct=1
```

使用 Direct I/O。

目的：

避免 Linux Page Cache 對結果產生過大影響。

否則可能測到：

```text
RAM Cache Speed
```

而不是實際 Storage I/O。


---

## --runtime

```bash
--runtime=60
```

Benchmark 持續：

```text
60 seconds
```


---

## --time_based

代表 fio 按照指定時間持續執行 workload。

即使已經跑完整個 1GB Working Set，
仍會繼續重複 I/O，
直到 Runtime 結束。


---

## --group_reporting

將 fio Job 結果整理成統一 Summary。


---

# Benchmark Result

執行：

```bash
/tmp/run_fio.sh 1G 60
```

測試時間：

```text
60 seconds
```

Workload：

```text
4KB Mixed Read / Write
Direct I/O
```


---

# Read Result

## Read IOPS

```text
1128 IOPS
```

意思：

每秒約完成：

```text
1128 次 Read I/O
```

每次：

```text
4KB
```


---

## Read Bandwidth

```text
4512 KiB/s
```

約：

```text
4.4 MiB/s
```

意思：

每秒讀取約 4.4 MiB 資料。


IOPS 與 Bandwidth 關係：

```text
1128 IOPS × 4KB

≈ 4512 KiB/s
```

因此結果一致。


---

## Read Average Latency

```text
437.99 usec
```

換算：

```text
0.438 ms
```

代表：

一次 Read I/O 平均約等待：

```text
0.44 ms
```


---

## Read p95 Latency

```text
644 usec
```

約：

```text
0.644 ms
```

代表：

95% Read I/O

在：

```text
0.644 ms
```

以內完成。


---

## Read p99 Latency

```text
898 usec
```

約：

```text
0.898 ms
```

代表：

99% Read I/O

在約：

```text
0.9 ms
```

內完成。


---

# Write Result

## Write IOPS

```text
1122 IOPS
```

代表：

每秒約完成：

```text
1122 次 Write I/O
```


---

## Write Bandwidth

```text
4490 KiB/s
```

約：

```text
4.4 MiB/s
```


---

## Write Average Latency

```text
444.73 usec
```

約：

```text
0.445 ms
```


---

## Write p95 Latency

```text
586 usec
```

約：

```text
0.586 ms
```


---

## Write p99 Latency

```text
775 usec
```

約：

```text
0.775 ms
```


---

# Result Summary

| Metric | Read | Write |
|---|---:|---:|
| IOPS | 1128 | 1122 |
| Bandwidth | 4512 KiB/s | 4490 KiB/s |
| Avg Latency | 0.438 ms | 0.445 ms |
| p95 Latency | 0.644 ms | 0.586 ms |
| p99 Latency | 0.898 ms | 0.775 ms |


---

# Why Bandwidth Is Only Around 4.5 MiB/s?

本次設定：

```text
Block Size:
4KB

Workload:
Mixed Read / Write

Direct I/O:
Enabled
```

這不是最大 Sequential Throughput Benchmark。

4KB Small I/O workload 更重視：

```text
IOPS
+
Latency
```

而不是最大 MB/s。


如果改成：

```text
Sequential Read
Block Size = 1MB
```

Bandwidth 通常會明顯提升。


因此：

不能只看到：

```text
4.5 MiB/s
```

就直接認為 Storage 很慢。

必須先看：

```text
Benchmark workload configuration
```


---

# IOPS vs Bandwidth

## IOPS

```text
Input / Output Operations Per Second
```

代表：

每秒可以完成多少次 I/O。

適合觀察：

- Database
- Small File
- Random I/O


---

## Bandwidth

代表：

每秒能傳輸多少資料。

單位：

```text
MiB/s
GB/s
```

適合觀察：

- Large Dataset Loading
- Model Loading
- Sequential File Access


---

# Latency

Latency 代表：

一次 I/O 從送出到完成需要多久。

本次平均：

```text
Read:
0.438 ms

Write:
0.445 ms
```

Latency 越低，
代表 Storage Response 越快。


---

# CPU Usage

fio 結果：

```text
usr:
1.89%

sys:
8.58%
```

代表：

fio 主要時間不是花在 CPU 計算。

而是在等待：

```text
Storage I/O
```

因此這是一個 I/O-oriented workload。


---

# Observation

本次測試驗證：

## 1. fio 可以模擬不同 Storage Workload

透過：

```text
rw
bs
size
runtime
```

可以建立不同 I/O Pattern。


---

## 2. 小 Block Size 更著重 IOPS

本次：

```text
4KB
```

因此主要觀察：

```text
IOPS
Latency
```

而不是最大 Sequential Bandwidth。


---

## 3. Direct I/O 避免 Cache 干擾

使用：

```bash
--direct=1
```

降低 Linux Page Cache 對測試的影響。


---

## 4. Container Storage 仍來自 Node

架構：

```text
fio

↓

Container Filesystem

↓

Kubernetes Node

↓

Node Storage
```

和 CPU Benchmark 相同：

Pod 本身沒有獨立 Storage Hardware。


---

# HPC AI Performance Insight

AI 系統效能可能不是 GPU 本身造成。

例如：

```text
Storage Throughput 不足

↓

Dataset Loading 變慢

↓

GPU 等待資料

↓

GPU Utilization 降低

↓

Training Performance 下降
```

因此 End-to-End Performance Analysis 必須同時觀察：

- CPU
- Memory
- Storage
- Network
- GPU


---

# Interview Questions

## Q1

fio 的 IOPS 與 Bandwidth 有什麼不同？

Answer:

IOPS 表示每秒完成多少次 I/O operation，
Bandwidth 表示每秒總共傳輸多少資料。

Small Block workload 通常較著重 IOPS，
Large Sequential workload通常較著重 Bandwidth。


---

## Q2

為什麼 fio Benchmark 常使用 direct=1？

Answer:

因為 Linux Page Cache 可能讓 I/O request 直接由 Memory 回應，
導致測到 Cache Performance 而非實際 Storage Performance。

Direct I/O 可以降低 Cache 對結果的影響。


---

# Completed

Week13 Day7-2 完成：

- 安裝 fio
- 建立 Storage Benchmark Script
- 建立 1GB Working Set
- 執行 4KB Mixed Read / Write Benchmark
- 分析 IOPS
- 分析 Bandwidth
- 分析 Latency
- 理解 Container Storage 與 Node Storage 關係


---

# Next

Week13 Day7-3：

```text
Network Benchmark
```

Tool：

```text
iperf3
```

目標：

分析：

- Network Throughput
- TCP Bandwidth
- Pod-to-Pod Network Performance
