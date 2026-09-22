<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-3 — Network benchmark 子章

[上一課](<day7-2-storage-benchmark.md>) · [本週目錄](README.md) · [下一課](<day7-4-benchmark-framework.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

iperf3 量測指定端點間的串流傳輸，結果受路徑、CPU、stream 數與協定影響。單向 TCP 吞吐不能證明 MPI 小訊息延遲或 RDMA 性能。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[benchmark/network/run_iperf3.sh](<../../benchmark/network/run_iperf3.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
# 效能測試腳本（run_iperf3）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

SERVER=${1:-iperf3-server}
TIME=${2:-30}

echo "================================"
echo " Network Benchmark"
echo "================================"

echo "Server : ${SERVER}"
echo "Runtime: ${TIME}s"

echo ""

# 網路吞吐測試：-c 指定伺服器，-t 指定測試秒數。
iperf3 \
    -c ${SERVER} \
    -t ${TIME}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day7-3-network-benchmark.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-3 - Network Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/network/results/iperf3_20260810.md](../../benchmark/network/results/iperf3_20260810.md)
- [benchmark/network/run_iperf3.sh](../../benchmark/network/run_iperf3.sh)：網路吞吐測試
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口

---

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
