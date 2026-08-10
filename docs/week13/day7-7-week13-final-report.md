# Week13 Day7-7 - Week13 Final Report

# Week13 Objective

完成 HPC AI Benchmark Platform 第一版。

本週目標：

建立可重複執行的 Benchmark Framework，

並完成：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Network Benchmark

最後整合為統一 Benchmark Framework。

---

# Week13 Architecture

```text
                  Benchmark Runner

                        │

                   run_all.sh

                        │

      ┌─────────┬─────────┬──────────┬──────────┐

      │         │         │          │

     CPU     Storage   PostgreSQL  Network

      │         │         │          │

 stress-ng      fio     pgbench    iperf3

      │         │         │          │

      └─────────┴─────────┴──────────┘

                        │

                 Result Collection

                        │

             results/<timestamp>/

                        │

       cpu.log
       storage.log
       postgres.log
       network.log
```

---

# Platform Components

Benchmark Runner

```text
benchmark Pod
```

Framework

```text
run_all.sh
```

CPU

```text
stress-ng
```

Storage

```text
fio
```

Database

```text
pgbench
```

Network

```text
iperf3
```

---

# Week13 Completed

## CPU Benchmark

Tool

```text
stress-ng
```

完成：

- CPU Stress Test
- Multi Worker
- CPU Throughput
- CPU Benchmark Script

---

## Storage Benchmark

Tool

```text
fio
```

完成：

- Random Read/Write
- IOPS
- Bandwidth
- Latency
- Storage Benchmark Script

---

## PostgreSQL Benchmark

Tool

```text
pgbench
```

完成：

- TPS
- Latency
- Client Benchmark
- PostgreSQL Benchmark Script

---

## Network Benchmark

Tool

```text
iperf3
```

完成：

- TCP Throughput
- Sender
- Receiver
- Retransmission
- Kubernetes Service Benchmark

---

# Benchmark Framework

Framework：

```text
run_all.sh
```

功能：

- Execute Benchmark
- PASS / FAIL
- Fail Fast
- Exit Code Validation
- Benchmark Summary

---

# Result Integration

Framework：

每次執行：

建立：

```text
results/<timestamp>/
```

Result：

```text
cpu.log

storage.log

postgres.log

network.log
```

所有 Benchmark：

集中保存。

---

# Framework Design

Benchmark Module：

只負責：

```text
Run Benchmark
```

Framework：

負責：

```text
Run

↓

Collect

↓

Save

↓

Summary
```

完成：

Separation of Responsibilities。

---

# Week13 Skills

完成：

Linux

- stress-ng
- fio
- iperf3
- pgbench

Kubernetes

- Benchmark Runner
- Service
- Pod Communication

Shell

- Function
- Exit Code
- pipefail
- tee
- Framework Design

Performance Engineering

- CPU
- Storage
- Database
- Network

---

# Platform Capability

目前平台：

已具備：

✅ CPU Benchmark

✅ Storage Benchmark

✅ PostgreSQL Benchmark

✅ Network Benchmark

✅ Benchmark Runner

✅ Benchmark Framework

✅ Result Collection

✅ Benchmark History

---

# Week13 Directory

```text
benchmark/

├──cpu/
│
├──storage/
│
├──postgres/
│
├──network/
│
├──results/
│
└──run_all.sh
```

---

# Platform Improvement

目前：

Framework Version

```text
v2
```

下一階段：

- Python Benchmark Framework
- JSON Output
- HTML Report
- Benchmark Dashboard
- Grafana Integration
- Historical Comparison

---

# Interview Questions

## Q1

為什麼建立 Benchmark Framework？

Answer：

統一管理不同 Benchmark，

降低人工操作，

提高 Benchmark Automation。

---

## Q2

為什麼需要 Benchmark Runner？

Answer：

建立固定 Runtime，

避免每次重新建立 Benchmark Environment。

---

## Q3

Framework 與 Benchmark Module 如何分工？

Answer：

Module：

只負責執行 Benchmark。

Framework：

負責：

- Execute
- Error Handling
- Result Collection
- Summary

---

## Q4

為什麼使用 tee？

Answer：

同時：

輸出 Terminal

與

保存 Log。

---

## Q5

為什麼使用 pipefail？

Answer：

避免：

Pipeline 中：

Benchmark Fail，

但 tee Success，

造成誤判。

---

# Week13 Conclusion

Week13 完成 HPC AI Benchmark Platform 第一版。

建立：

- Modular Benchmark Architecture
- Benchmark Framework
- Result Integration
- Benchmark Runner
- Performance Baseline

平台已具備 CPU、Storage、Database、Network Benchmark 能力。

下一週將進入 GPU Platform，加入 CUDA、GPU Monitoring 與 GPU Performance Benchmark。
