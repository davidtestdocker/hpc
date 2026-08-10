# Week13 Day7-4 - Benchmark Framework Integration

## 今天平台增加了什麼？

本次完成 HPC AI Benchmark Framework 第一版。

原本：

每個 Benchmark 都需要手動執行。

例如：

```text
stress-ng

fio

pgbench

iperf3
```

現在：

```text
run_all.sh

↓

CPU Benchmark

↓

Storage Benchmark

↓

PostgreSQL Benchmark

↓

Network Benchmark
```

透過一個入口即可完成所有 Benchmark。

---

# Architecture

```text
               Benchmark Runner

                    │

               run_all.sh

                    │

    ┌────────┬────────┬────────┬────────┐

    │        │        │        │

 CPU      Storage  PostgreSQL Network

    │        │        │        │

stress-ng   fio    pgbench   iperf3
```

Framework：

負責：

- 呼叫各 Benchmark
- 控制 Benchmark 順序
- 建立統一入口

---

# Benchmark Directory

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

目前所有 Benchmark

皆以 Module 管理。

---

# Benchmark Runner

Benchmark Pod：

```text
benchmark
```

用途：

```text
Benchmark Runner
```

負責：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Network Benchmark

所有 Benchmark

皆於同一個 Pod 執行。

---

# Benchmark Flow

```text
run_all.sh

↓

CPU Benchmark

↓

Storage Benchmark

↓

PostgreSQL Benchmark

↓

Network Benchmark

↓

Finish
```

Framework

負責：

依照固定順序執行所有 Benchmark。

---

# Why Benchmark Runner?

如果每次：

```text
kubectl exec

↓

執行一個 Tool

↓

離開

↓

再進 Pod

↓

再執行下一個 Tool
```

效率很差。

建立 Benchmark Runner 後：

所有 Benchmark

統一於：

```text
benchmark Pod
```

完成。

---

# Benchmark Image

目前：

使用：

```text
debian:12
```

第一次建立：

需要：

```text
apt install

stress-ng

fio

iperf3

postgresql-client
```

原因：

Container

屬於：

```text
Ephemeral
```

Pod 重建：

所有套件消失。

---

未來 Production：

將建立：

```text
benchmark-runner Image
```

預先安裝：

- stress-ng
- fio
- iperf3
- pgbench

避免：

每次重新安裝。

---

# run_all.sh

目前：

```bash
./run_all.sh
```

即可依序執行：

- CPU
- Storage
- PostgreSQL
- Network

建立統一 Benchmark Entry Point。

---

# Observation

完成：

- Benchmark Runner Pod
- Benchmark Framework
- 統一 Benchmark Script
- Modular Benchmark Design

目前 Framework

已具備：

CPU

Storage

Database

Network

四種 Benchmark。

---

# HPC AI Performance Insight

大型 HPC AI Platform

通常不會：

人工逐一執行 Benchmark。

而會：

```text
Framework

↓

Scheduler

↓

Benchmark

↓

Result

↓

Report
```

目前平台：

已建立：

Framework 雛形。

---

# Interview Questions

## Q1

為什麼需要 Benchmark Framework？

Answer：

避免人工逐一執行 Benchmark。

建立統一入口，

提高自動化程度。

---

## Q2

為什麼使用 Benchmark Runner Pod？

Answer：

所有 Benchmark Tool

集中於同一個 Runtime。

避免：

不同 Pod

造成環境差異。

---

# Completed

Week13 Day7-4 完成：

- 建立 Benchmark Runner
- 建立統一 Benchmark Framework
- 建立 run_all.sh
- 完成 CPU / Storage / PostgreSQL / Network 整合
- 建立 Modular Benchmark Architecture

---

# Next

Week13 Day7-5

Benchmark Framework v2

新增：

- PASS / FAIL
- Summary
- Exit Code
- Fail Fast
