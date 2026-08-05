# Week12 Day4 - Linux Historical Performance Analysis

## 目標

本章節學習使用 `sar`（System Activity Reporter）分析 Linux 系統歷史效能資料，了解 `sar` 的工作原理，以及如何查看 CPU、Memory、Disk、Network 的歷史資訊。

完成本章後，可以回答：

- `sar` 是什麼？
- `sar` 與 `top` 有什麼差異？
- `sar` 的資料從哪裡來？
- `sysstat` 與 `sadc` 的角色是什麼？
- 為什麼 `sar` 看不到剛剛幾秒鐘前的 CPU 尖峰？

---

# 今日學習重點

- 認識 Historical Performance Analysis
- 了解 `sar` 工作原理
- 了解 `sysstat`、`sadc`
- systemd timer
- `sar -u`
- `sar -P ALL`
- Production Incident Analysis

---

# Lab Environment

OS

```text
Ubuntu 24.04
```

CPU

```text
4 vCPU
```

Memory

```text
16GB
```

---

# 為什麼需要 sar？

前幾天學過：

- top
- free
- vmstat
- iostat

這些工具都有共同特性：

> **只能查看目前系統狀態。**

例如：

今天上午收到通知：

```
昨天晚上 22:30 API Timeout
```

登入主機：

```bash
top
```

看到：

```
CPU Idle 95%
```

並不能代表：

```
昨天晚上 CPU 沒有滿載。
```

因此需要：

```
sar
```

查看歷史資料。

---

# sar 是什麼？

sar

(System Activity Reporter)

屬於：

```
sysstat
```

工具之一。

用途：

讀取 Linux 歷史效能資料。

---

# sar 的工作流程

```
systemd timer
        │
        ▼
sysstat-collect.timer
        │
        ▼
sysstat-collect.service
        │
        ▼
sadc
        │
        ▼
/var/log/sysstat/saXX
        │
        ▼
sar
```

重點：

- `sar` 不負責收集資料。
- `sadc` 才是真正收集資料。
- `sar` 只是讀取 `saXX`。

---

# Step1：確認 sar

查看版本：

```bash
sar -V
```

---

# Step2：確認 sysstat

查看：

```bash
systemctl status sysstat
```

若尚未啟用：

```bash
sudo systemctl enable --now sysstat
```

---

# Step3：確認 Timer

```bash
systemctl list-timers | grep sysstat
```

Ubuntu 24.04：

```
sysstat-collect.timer
```

代表：

系統定期收集資料。

---

# Step4：查看歷史資料

查看：

```bash
ls -lh /var/log/sysstat/
```

例如：

```
sa04
```

代表：

本月第 4 天收集的資料。

---

# Ubuntu 預設收集頻率

查看：

```bash
systemctl cat sysstat-collect.timer
```

重要設定：

```text
OnCalendar=*:00/10
```

代表：

```
每 10 分鐘
```

收集一次。

因此：

```
sar
```

較適合：

- Production Trend
- Incident Analysis

而不是：

```
幾秒鐘內的 CPU 尖峰
```

---

# Step5：查看 CPU

```bash
sar -u
```

重要欄位：

| 欄位 | 說明 |
|------|------|
| %user | User Space CPU |
| %system | Kernel CPU |
| %iowait | Waiting Disk |
| %idle | CPU Idle |

---

# Step6：查看每顆 CPU

```bash
sar -P ALL
```

與：

```
mpstat
```

不同：

- mpstat：即時
- sar：歷史

---

# sar 與其他工具

| 工具 | 用途 |
|------|------|
| top | 即時 CPU / Memory |
| free | 即時 Memory |
| vmstat | 即時 CPU / Memory / IO |
| iostat | 即時 Disk |
| pidstat | 即時 Process |
| sar | 歷史效能分析 |

---

# Production Incident

例如：

```
昨天晚上 22:30 API Timeout
```

分析流程：

```
確認時間
      │
      ▼
sar
      │
CPU 是否異常？
      │
      ▼
Memory 是否異常？
      │
      ▼
Disk 是否異常？
      │
      ▼
Network 是否異常？
      │
      ▼
若需要即時分析
      │
      ▼
top
pidstat
perf
strace
```

---

# 今日重點

- `sar` 是歷史分析工具。
- `sar` 不負責收集資料。
- `sadc` 才是真正收集資料。
- Ubuntu 預設透過 systemd timer 每 10 分鐘收集一次。
- `sar` 適合分析長時間趨勢，不適合分析幾秒鐘的尖峰。

---

# Interview

## Q1：`sar` 與 `top` 有什麼差異？

**答：**

`top` 只能查看目前系統狀態；`sar` 可以讀取 `sysstat` 收集的歷史資料，因此適合分析過去某個時間點的 CPU、Memory、Disk、Network 狀況。

---

## Q2：`sar` 的資料是哪裡來的？

**答：**

`sar` 本身不會收集資料，而是讀取 `sysstat` 使用 `sadc` 定期收集並寫入 `/var/log/sysstat/saXX` 的歷史效能資料。在 Ubuntu 24.04 中，預設由 `sysstat-collect.timer` 每 10 分鐘觸發一次資料收集。
