<!-- readable-curriculum: 2026-09-22 -->
# Week12 Day3 — Disk 分析

[上一課](<Day2-Linux-Memory-Performance-Analysis.md>) · [本週目錄](README.md) · [下一課](<Day4-Linux-Historical-Performance-Analysis.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

I/O 小區塊隨機存取與大區塊循序讀寫會得到不同 IOPS／吞吐。fio 的 size、rw、bs、iodepth、direct 共同定義測試，不能只報一個 MB/s。

## 在現在的專案中

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week12/Day3-Linux-Disk-Performance-Analysis.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 診斷方法繼續適用；舊 perf／strace／CPU 數據不代表主 MPI 的自動 profiling。
> **閱讀順序**：先學本文基礎，再讀[Week12 現行對照與檢核](../learning-guide.md#week12)及[對應現行入口](../performance/performance-report.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week12 Day3：Linux Disk Performance Analysis

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[performance-report](../performance/performance-report.md)。

---

## 今日目標

學習 Linux Disk Performance Analysis，了解如何判斷磁碟是否為系統瓶頸，並熟悉 Linux 常用的磁碟效能分析工具。

---

# 今日學習重點

- 認識 Linux Block Device
- 了解 Disk Throughput、IOPS、Latency
- 學會使用 lsblk、df、mount 查看磁碟資訊
- 學會使用 iostat 分析磁碟效能
- 學會使用 fio 建立磁碟壓力測試
- 分析 Sequential 與 Random I/O 差異

---

# 環境資訊

```
OS Disk
/dev/sda
30GB
ext4

Data Disk
/dev/sdb
100GB
ext4
```

Root Disk：

- 儲存 Linux
- Kubernetes
- Container Overlay

Data Disk：

- Benchmark
- PostgreSQL
- 測試資料

---

# 查看磁碟資訊

## lsblk

查看磁碟、Partition、Mount Point。

```bash
lsblk
```

---

## df -h

查看容量使用情況。

```bash
df -h
```

重點：

- Size
- Used
- Available
- Use%

一般建議：

- <80%：正常
- 80~90%：開始注意
- >95%：建議清理

---

## mount

查看檔案系統與掛載方式。

```bash
mount | grep "^/dev"
```

常見：

- ext4
- xfs

---

# Disk Performance

Disk Performance 主要觀察三個指標。

## 1. Bandwidth

代表：

每秒可傳輸多少資料。

單位：

```
MB/s
```

適合觀察：

- 大檔案複製
- Backup
- AI Model Loading

---

## 2. IOPS

Input Output Operations Per Second

代表：

每秒完成多少次 IO。

```
IOPS

=

Read IOPS

+

Write IOPS
```

適合：

- PostgreSQL
- MySQL
- Redis
- etcd

---

## 3. Latency

代表：

一次 IO 完成需要多久。

Linux：

```
await
```

越低越好。

一般 SSD：

- <1ms：很好
- 1~5ms：正常
- >20ms：偏高
- >50ms：可能發生瓶頸

---

# iostat

安裝：

```bash
sudo apt install sysstat
```

執行：

```bash
iostat -dx 1 5
```

重點欄位：

| 欄位 | 說明 |
|------|------|
| r/s | 每秒 Read 次數 |
| w/s | 每秒 Write 次數 |
| rkB/s | 每秒 Read KB |
| wkB/s | 每秒 Write KB |
| await | IO Latency |
| aqu-sz | Queue Length |
| %util | Disk Busy Percentage |

---

# fio Benchmark

確認版本：

```bash
fio --version
```

---

## Sequential Write

```bash
fio --name=seq-write \
    --directory=/data \
    --filename=seq-write-test \
    --size=1G \
    --bs=1M \
    --rw=write \
    --direct=1 \
    --ioengine=libaio \
    --iodepth=16 \
    --numjobs=1 \
    --runtime=30 \
    --time_based
```

觀察：

- Bandwidth
- Throughput
- Disk Utilization

本次測試：

```
Bandwidth

177 MiB/s
≈185 MB/s
```

代表：

磁碟每秒可持續寫入約 185MB。

---

## Random Read

```bash
fio --name=rand-read \
    --directory=/data \
    --filename=rand-test \
    --size=2G \
    --bs=4k \
    --rw=randread \
    --direct=1 \
    --ioengine=libaio \
    --iodepth=32 \
    --numjobs=1 \
    --runtime=30 \
    --time_based
```

用途：

模擬：

- PostgreSQL
- MySQL
- Redis
- etcd

Random IO 比 Sequential 更接近真實 Production Workload。

---

# Sequential vs Random

Sequential：

```
□□□□□□□□□□□□
```

連續讀寫。

優點：

Bandwidth 高。

---

Random：

```
□ □ □ □ □ □
```

隨機跳躍。

特性：

- Bandwidth 較低
- IOPS 較重要
- Latency 更重要

---

# 今日重點整理

Bandwith

- 每秒搬多少資料
- 單位 MB/s

IOPS

- 每秒完成多少次 IO

Latency

- 每次 IO 花多久時間

Queue

- 有多少 IO 正在等待

%util

- Disk 忙碌程度
- 不可單獨判斷是否發生瓶頸

---

# 面試常見問題

## Q1

Bandwidth、IOPS、Latency 有什麼差別？

答：

Bandwidth 表示每秒傳輸多少資料，IOPS 表示每秒完成多少次 I/O，Latency 表示一次 I/O 完成所需時間。大型檔案傳輸通常看 Bandwidth，資料庫與 Kubernetes 等隨機存取工作則更重視 IOPS 與 Latency。

---

## Q2

Linux 如何分析磁碟是否發生瓶頸？

答：

使用 `iostat -dx` 觀察 `await`、`%util`、`r/s`、`w/s`、`rkB/s`、`wkB/s` 等指標，再搭配 `fio` 建立壓力測試，綜合判斷 Throughput、IOPS、Latency 是否符合預期，而不是只看 `%util`。
