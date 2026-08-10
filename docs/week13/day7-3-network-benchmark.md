# Week13 Day7-3 - Network Benchmark

## 今天平台增加了什麼？

本次加入 Network Benchmark Module。

使用 iperf3 建立 Client / Server 網路壓力測試，
量測 Kubernetes Pod 與 Pod 之間的 TCP Throughput。

目前 Benchmark Framework 已完成：

- CPU Benchmark
- Storage Benchmark
- PostgreSQL Benchmark
- Redis Benchmark
- Network Benchmark

---

# Architecture

```text
                   GKE Cluster

        ┌──────────────────────────────┐
        │                              │
        │ Primary Pool Node            │
        │                              │
        │ benchmark Pod (Client)       │
        │          │                   │
        │          │ TCP Traffic       │
        │          ▼                   │
        │  iperf3-server Service       │
        │          │                   │
        │          ▼                   │
        │  iperf3-server Pod           │
        │                              │
        └──────────────────────────────┘
```

Benchmark 流程：

```text
benchmark Pod

↓

iperf3 Client

↓

Service DNS

↓

iperf3 Server

↓

Network Performance
```

---

# 為什麼需要 Server？

Network Benchmark 與 CPU Benchmark 不同。

CPU：

```text
stress-ng

↓

CPU
```

Storage：

```text
fio

↓

Storage
```

Network：

一定需要：

```text
Sender

↓

Receiver
```

因此：

benchmark Pod

```text
Client
```

iperf3-server Pod

```text
Server
```

Client 持續送資料給 Server。

Server 計算：

- Throughput
- Bandwidth
- TCP Statistics

---

# 為什麼建立 Kubernetes Service？

如果直接連 Pod IP：

例如：

```text
10.68.0.23
```

Pod 重建後：

```text
10.68.0.61
```

IP 就改變。

因此建立：

```text
Service

iperf3-server
```

Client 永遠只需要：

```bash
iperf3 -c iperf3-server
```

DNS：

```text
iperf3-server

↓

ClusterIP

↓

真正 Pod
```

不用知道 Pod IP。

---

# Environment

Namespace

```text
hpc-platform-dev
```

Benchmark Pod

```text
benchmark
```

iperf3 Server

```text
iperf3-server
```

Service

```text
iperf3-server
```

Tool

```text
iperf3 3.12
```

---

# Benchmark Script

位置：

```text
benchmark/network/run_iperf3.sh
```

內容：

```bash
#!/bin/bash

set -e

SERVER=${1:-iperf3-server}
TIME=${2:-30}

echo "================================"
echo " Network Benchmark"
echo "================================"

echo "Server : ${SERVER}"
echo "Runtime: ${TIME}s"

echo ""

iperf3 \
  -c ${SERVER} \
  -t ${TIME}
```

執行：

```bash
./run_iperf3.sh iperf3-server 30
```

---

# Parameter

## SERVER

```text
iperf3-server
```

代表：

Kubernetes Service 名稱。

不是 Pod IP。

Client：

```text
benchmark Pod

↓

iperf3-server Service

↓

iperf3-server Pod
```

---

## Runtime

```text
30 seconds
```

代表：

Benchmark 持續送 TCP 流量：

```text
30 秒
```

---

# Benchmark Result

Transfer

```text
65.7 GBytes
```

Bandwidth

```text
18.8 Gbits/sec
```

Sender

```text
18.8 Gbits/sec
```

Receiver

```text
18.8 Gbits/sec
```

Retr

```text
10367
```

---

# Result Analysis

## Transfer

Transfer：

```text
65.7 GBytes
```

代表：

30 秒內：

總共傳輸：

```text
65.7 GB
```

---

## Bandwidth

Bandwidth：

```text
18.8 Gbits/sec
```

注意：

單位：

```text
Gigabits

不是

Gigabytes
```

換算：

```text
18.8 Gbps

≈2.35 GB/s
```

代表：

Benchmark Pod 與 Server Pod

平均：

```text
約 2.35 GB/s
```

---

## Sender

Sender：

```text
18.8 Gbits/sec
```

代表：

Client 實際送出的速度。

---

## Receiver

Receiver：

```text
18.8 Gbits/sec
```

代表：

Server 實際接收速度。

Sender：

```text
≈
```

Receiver

表示：

Network Transmission 正常。

---

## Retr

Retr：

```text
10367
```

代表：

TCP Retransmission。

不是：

```text
10367 Packet Loss
```

Retr 可能原因：

- TCP Congestion Control
- Buffer 調整
- High Throughput
- Virtual Network Stack

本次：

Bandwidth 維持：

```text
18.8 Gbps
```

因此：

整體 Network Performance 正常。

---

# Observation

本次測試驗證：

## 1.

Kubernetes Service

可以提供固定存取入口。

Client 不需要知道 Pod IP。

---

## 2.

Pod 與 Pod

可以透過 Service 建立 TCP Communication。

---

## 3.

iperf3 可量測：

- Throughput
- TCP Bandwidth
- Retransmission

---

## 4.

本次：

Client

Server

皆位於：

```text
Primary Pool Node
```

因此：

主要測得：

```text
Same Node Pod-to-Pod Network
```

尚未測試：

```text
Cross Node Throughput
```

---

# HPC AI Performance Insight

AI Platform 不只有 CPU 與 GPU。

Distributed AI：

需要：

- NCCL
- MPI
- RDMA
- RoCE

都高度依賴：

```text
Network Throughput

+

Low Latency
```

Network Benchmark

是 HPC Performance Engineering 的重要項目。

---

# Interview Questions

## Q1

為什麼 iperf3 需要 Client 與 Server？

Answer：

Network Benchmark 必須有：

Sender

與

Receiver。

Client 負責送資料。

Server 負責接收並統計 Throughput。

---

## Q2

為什麼不直接連 Pod IP？

Answer：

Pod IP 會改變。

Service 提供固定 DNS 名稱。

Client 永遠只需要：

```text
iperf3-server
```

即可存取。

---

## Q3

Retr 是不是代表封包遺失？

Answer：

不是。

Retr 代表 TCP Retransmission。

可能因為：

- Congestion Control
- High Throughput
- Buffer 調整

不能直接等於 Packet Loss。

---

# Completed

Week13 Day7-3 完成：

- 建立 iperf3 Server
- 建立 Kubernetes Service
- 建立 Network Benchmark Script
- 完成 Pod-to-Pod Network Benchmark
- 分析 Throughput
- 分析 Sender / Receiver
- 分析 TCP Retransmission
- 建立 Network Benchmark Baseline

---

# Next

Week13 Day7-4

Benchmark Framework Integration

整合：

- CPU
- Storage
- PostgreSQL
- Redis
- Network

形成統一 Benchmark Framework。
