# Week12 Day3：Linux Disk Performance Analysis

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
