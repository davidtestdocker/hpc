# Week13 Day7-5 - Benchmark Framework v2

## 今天平台增加了什麼？

本次將 Benchmark Framework 從單純依序執行，
升級成具有執行狀態判斷的 Framework v2。

新增：

- PASS / FAIL
- Fail Fast
- Exit Code
- Benchmark Summary

讓 Framework 可以判斷每個 Benchmark 是否成功。


---

# Architecture

```text
                   run_all.sh

                       │

        ┌──────────────┼──────────────┐

        │              │              │

      CPU           Storage       PostgreSQL

        │              │              │

   stress-ng           fio          pgbench

        │              │              │

      PASS           PASS           PASS

                       │

                    Network

                       │

                    iperf3

                       │

                     PASS

                       │

                       ▼

                Benchmark Summary
```

---

# Why Framework v2?

原本 Framework v1：

```text
CPU

↓

Storage

↓

PostgreSQL

↓

Network

↓

Completed
```

問題：

如果 PostgreSQL Benchmark 失敗：

```text
PostgreSQL FAIL
```

Framework 仍可能繼續執行：

```text
Network
```

甚至最後仍顯示：

```text
Benchmark Completed
```

這會造成錯誤的測試結果。


---

# Framework v2

現在改成：

```text
Execute Benchmark

↓

Check Exit Code

↓

PASS / FAIL
```

如果 Benchmark 成功：

```text
Exit Code = 0

↓

PASS
```

如果失敗：

```text
Exit Code != 0

↓

FAIL

↓

Stop
```

---

# run_benchmark Function

Framework 建立：

```bash
run_benchmark() {
    NAME=$1
    COMMAND=$2

    echo ""
    echo "======================================"
    echo "${NAME}"
    echo "======================================"

    if eval "${COMMAND}"; then
        echo "[PASS] ${NAME}"
    else
        echo "[FAIL] ${NAME}"
        echo ""
        echo "Benchmark stopped because ${NAME} failed."
        exit 1
    fi
}
```

---

# NAME

第一個參數：

```text
Benchmark Name
```

例如：

```text
CPU Benchmark
```

---

# COMMAND

第二個參數：

```text
Benchmark Command
```

例如：

```bash
bash cpu/run_stress_ng.sh 2 30
```

---

# Exit Code

Linux command 執行完成後會產生：

```text
Exit Code
```

成功：

```text
0
```

失敗：

```text
非 0
```

Framework 使用：

```bash
if eval "${COMMAND}"
```

判斷 Benchmark 是否成功。


---

# Fail Fast

如果其中一個 Benchmark 失敗：

```bash
exit 1
```

Framework 立即停止。

例如：

```text
CPU
PASS

↓

Storage
PASS

↓

PostgreSQL
FAIL

↓

STOP
```

Network 不再繼續執行。

這種設計稱為：

```text
Fail Fast
```

---

# Benchmark Modules

目前 Framework 包含：

```text
CPU Benchmark
```

Tool：

```text
stress-ng
```

---

```text
Storage Benchmark
```

Tool：

```text
fio
```

---

```text
PostgreSQL Benchmark
```

Tool：

```text
pgbench
```

---

```text
Network Benchmark
```

Tool：

```text
iperf3
```

---

# Execution

在 Benchmark Runner Pod：

```bash
cd /tmp/benchmark
```

執行：

```bash
./run_all.sh
```

---

# Successful Result

本次 Framework 執行結果：

```text
[PASS] CPU Benchmark

[PASS] Storage Benchmark

[PASS] PostgreSQL Benchmark

[PASS] Network Benchmark
```

最後：

```text
======================================
 Benchmark Summary
======================================

CPU          PASS
Storage      PASS
PostgreSQL   PASS
Network      PASS

All benchmarks completed successfully.
```

---

# Benchmark Flow

```text
run_all.sh

↓

CPU Benchmark

↓

Check Exit Code

↓

PASS

↓

Storage Benchmark

↓

Check Exit Code

↓

PASS

↓

PostgreSQL Benchmark

↓

Check Exit Code

↓

PASS

↓

Network Benchmark

↓

Check Exit Code

↓

PASS

↓

Summary
```

---

# Why PASS / FAIL Matters

Performance Benchmark 不只是：

```text
取得數字
```

還必須確定：

```text
Benchmark 是否真的成功
```

例如：

PostgreSQL 曾發生：

```text
password authentication failed
```

如果沒有狀態判斷：

Framework 可能：

```text
產生錯誤 Report
```

加入 PASS / FAIL 後：

Framework 可以阻止無效 Benchmark Result。


---

# Platform Engineering Insight

Benchmark Framework 與一般 shell script 的差別：

一般 Script：

```text
Command A

Command B

Command C
```

Framework：

```text
Execute

↓

Validate

↓

Handle Error

↓

Collect Status

↓

Generate Summary
```

因此 Framework 不只是執行工具，

還需要：

- Execution Control
- Error Handling
- Status Management
- Result Management


---

# Current Framework

```text
benchmark/

├── cpu/
│   └── run_stress_ng.sh
│
├── storage/
│   └── run_fio.sh
│
├── postgres/
│   └── run_pgbench.sh
│
├── network/
│   └── run_iperf3.sh
│
├── k8s/
│
└── run_all.sh
```

---

# Interview Questions

## Q1

為什麼 Benchmark Framework 需要 Fail Fast？

Answer：

如果 Benchmark 中途失敗，

後續結果可能失去可信度。

Fail Fast 可以：

立即停止流程，

避免產生錯誤 Benchmark Report。


---

## Q2

Linux Exit Code 有什麼用途？

Answer：

Exit Code 用來表示 command 執行狀態。

```text
0
```

代表成功。

非 0：

代表失敗。

Automation Framework 可以透過 Exit Code：

判斷：

PASS / FAIL。


---

# Completed

Week13 Day7-5 完成：

- Benchmark Framework v2
- PASS / FAIL
- Exit Code Validation
- Fail Fast
- Benchmark Summary
- 四個 Benchmark Module 全部成功執行


---

# Next

Week13 Day7-6

Benchmark Result Integration

目標：

將：

```text
CPU
Storage
PostgreSQL
Network
```

的 Result

集中保存與整理，

讓 Framework 不只：

```text
Run Benchmark
```

還可以：

```text
Collect Result
```
