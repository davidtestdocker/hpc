# Week 1 Day 6－Disk I/O（磁碟輸入/輸出）

[上一課](<day5-memory.md>) · [本週目錄](README.md) · [下一課](<day7-performance-analysis.md>)

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

## 補充：2026-09-23 實際執行與解讀

以下是助理在目前 Linux 工作環境新執行的結果，原有教材與舊觀察保留在上方。這次程序清單受執行沙箱限制；整機 CPU、記憶體與裝置統計的可見範圍不一定與程序清單相同。不能把新結果冒充當年的 VM 紀錄。

各指令的時間、參數與結束碼見 [執行紀錄](results/20260923/execution.json)。

### `df -h`

以下摘錄表頭、根目錄與 `/data`，其他掛載見 [完整輸出](results/20260923/df-h.stdout.txt)。

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        29G   23G  6.8G  77% /
/dev/sdb1        98G  3.1G   90G   4% /data
```

根目錄本次使用率為 77%、可用 6.8G；`/data` 為另一個掛載點。這是容量資訊，沒有量出讀寫延遲。

### `lsblk`

```text
NAME    MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
loop0     7:0    0 66.8M  1 loop /snap/core24/1643
loop1     7:1    0 66.8M  1 loop /snap/core24/2124
loop2     7:2    0 50.1M  1 loop /snap/snapd/27710
loop3     7:3    0 50.3M  1 loop /snap/snapd/27738
sda       8:0    0   30G  0 disk
├─sda1    8:1    0 29.9G  0 part /tmp/codex-bwrap-synthetic-mount-targets-0
│                                /tmp
│                                /root/.codex
│                                /root
│                                /
├─sda14   8:14   0    4M  0 part
└─sda15   8:15   0  106M  0 part /boot/efi
sdb       8:16   0  100G  0 disk
└─sdb1    8:17   0  100G  0 part /data
```

[完整輸出](results/20260923/lsblk.stdout.txt)。

本次已能看到 `sdb1` 掛在 `/data`，與舊文未列分割區的 sdb 不同。舊輸出缺少掛載點本身，也不足以證明磁碟沒有資料。

### `iostat`

```text
Linux 6.8.0-1067-gcp (hpc-demo) 	09/23/26 	_x86_64_	(4 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           3.45    0.10    2.09    0.29    0.08   93.99

Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd
loop0             0.03         0.50         0.00         0.00       1066          0          0
loop1             0.03         0.51         0.00         0.00       1084          0          0
loop2             0.02         0.16         0.00         0.00        346          0          0
loop3             0.27         9.77         0.00         0.00      20791          0          0
loop4             0.01         0.01         0.00         0.00         14          0          0
sda              28.29       849.83      1025.27       762.49    1807988    2181249    1622180
sdb               0.11         2.62         0.01         0.00       5569         12          0
```

[完整輸出](results/20260923/iostat.stdout.txt)。

單次、不帶間隔的 iostat 這裡顯示開機以來的平均，`%iowait` 為 0.29；它不是剛剛某個工作的專屬等待時間。低 iowait 不能支持舊文「不存在 Disk Bottleneck」的結論，還要看對應工作的延遲與裝置統計。原文 `apt install -y sysstat` 是安裝步驟；本次 iostat 已存在，因此沒有重複安裝。
