<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day6 — Disk I/O

[上一課](<day5-memory.md>) · [本週目錄](README.md) · [下一課](<day7-performance-analysis.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材數值摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

修正原文「目前不存在 Disk Bottleneck」的過度結論：低 iowait 不能排除個別工作 I/O 延遲問題。lsblk 沒顯示 mountpoint 不代表磁碟一定空白或可安全格式化。Redis PVC 是後續配置，沒有產生這份 Week1 iostat 結果。

## 程式／設定與來源

本次核對：[helm/redis/templates/pvc.yaml](<../../helm/redis/templates/pvc.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<day6-disk-io.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
%iowait = 0.04%
```

原文另保存 /dev/root 容量 29G、Used 6.5G、Avail 23G，以及 lsblk 摘錄。容量充足和一次低 iowait 是兩個觀察，不能合成磁碟已經過性能驗收。

**仍缺的證據／不能證明的事：** 缺 per-device await／queue／吞吐、量測 workload 與時間範圍；不新增不存在的 disk benchmark 結論。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 6－Disk I/O（磁碟輸入/輸出）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day3-Linux-Disk-Performance-Analysis](../week12/Day3-Linux-Disk-Performance-Analysis.md)。

---

## 今日目標

理解 Disk I/O 的概念，以及如何判斷系統是否因為磁碟而變慢。

---

# CPU 不會直接讀磁碟

程式執行流程：

```

Disk
│
▼
Linux Kernel
│
▼
Memory
│
▼
CPU

```

CPU 只能處理記憶體中的資料，因此程式必須先將資料從磁碟讀入 Memory。

---

# Disk I/O

Disk I/O（Input / Output）代表對磁碟進行讀寫。

例如：

- 讀取檔案
- 寫入 Log
- 存放 Benchmark 結果
- 載入 AI Model
- Database 存取

都屬於 Disk I/O。

---

# 查看磁碟容量

使用：

```bash
df -h
```

觀察：

```
Filesystem      Size  Used  Avail
/dev/root       29G   6.5G   23G
```

目前：

- 總容量：29GB
- 已使用：6.5GB
- 可使用：23GB

磁碟空間充足。

---

# 查看磁碟結構

使用：

```bash
lsblk
```

觀察：

```
sda
├── sda1  /
├── sda14
└── sda15

sdb
```

目前：

- Ubuntu 安裝於 sda1
- sdb 為尚未使用的第二顆磁碟

未來可作為：

- AI Model
- Benchmark Data
- Report
- Log

儲存空間。

---

# iostat

安裝：

```bash
apt install -y sysstat
```

使用：

```bash
iostat
```

本次觀察：

```
%iowait = 0.04%
```

代表：

CPU 幾乎沒有等待磁碟。

目前系統不存在 Disk Bottleneck。

---

# 今日重點

- CPU 不會直接讀取磁碟。
- Disk I/O 是所有讀寫磁碟的操作。
- `df -h` 用來查看磁碟容量。
- `lsblk` 用來查看磁碟與 Partition。
- `iostat` 可分析磁碟效能。
- `%iowait` 越高，代表 CPU 花越多時間等待磁碟。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- Benchmark Result
- AI Model
- Log
- Prometheus Data

都需要磁碟。

Performance Engineer 必須判斷：

- 是否磁碟容量不足？
- 是否磁碟 I/O 成為瓶頸？
- CPU 是否因等待磁碟而降低整體效能？

Disk Analysis 是 Performance Analysis 的重要組成之一。
