<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](<../../../learning-guide.md#week1>)及[對應現行入口](<../../../runbooks/ai-hpc-job-troubleshooting.md>)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 6－Disk I/O（磁碟輸入/輸出）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day3-Linux-Disk-Performance-Analysis](<../../../week12/Day3-Linux-Disk-Performance-Analysis.md>)。

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
