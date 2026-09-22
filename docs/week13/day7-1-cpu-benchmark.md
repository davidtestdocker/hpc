<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day7-1 — CPU benchmark 子章

[上一課](<day6-benchmark-automation.md>) · [本週目錄](README.md) · [下一課](<day7-2-storage-benchmark.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史CPU結果檔。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

103%不能直接斷言sampling variation，也需核對allocatable/capacity分母。bogo ops是工具特定計數，不是跨工具分數；2CPU node限制不是建立更多硬體。

## 程式／設定與來源

本次核對：[benchmark/cpu/run_stress_ng.sh](<../../benchmark/cpu/run_stress_ng.sh>)、[benchmark/k8s/benchmark-runner.yaml](<../../benchmark/k8s/benchmark-runner.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<../../benchmark/cpu/results/cpu_benchmark_20260810.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
2000m (103%)
```

20260810檔名、舊hpc-dev primary node；結果檔保存422m→2000m。92486在課文標Example，不能當raw。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day7-1 - CPU Benchmark

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/cpu/results/cpu_benchmark_20260810.md](../../benchmark/cpu/results/cpu_benchmark_20260810.md)
- [benchmark/cpu/run_stress_ng.sh](../../benchmark/cpu/run_stress_ng.sh)：CPU 壓測
- [benchmark/run_all.sh](../../benchmark/run_all.sh)：benchmark 整合入口

---

## 今天平台增加了什麼？

本次加入 CPU Benchmark Module。

使用 stress-ng 建立 CPU workload，
並透過 Kubernetes Node Metrics 觀察 CPU Saturation。

目前 Benchmark Framework 增加：

- CPU workload generation
- CPU resource observation
- CPU saturation analysis


---

# Architecture

```text
GKE Cluster

primary-pool Node VM
        |
        |
 benchmark Pod
        |
        |
 stress-ng
        |
        |
 Node VM CPU
```


Benchmark Pod 不擁有自己的 CPU hardware。

Pod 使用的是 Kubernetes Node 提供的 CPU 資源。


完整流程：

```text
stress-ng process

        ↓

Container

        ↓

Pod

        ↓

Kubernetes Node

        ↓

VM CPU
```


---

# Environment

## Kubernetes Namespace

```
hpc-platform-dev
```


## Benchmark Pod

```
benchmark
```


## Node

```
gke-hpc-dev-primary-pool-1489cf18-vxpk
```


## Node CPU Capacity

```
cpu: 2 cores
```


確認指令：

```bash
kubectl describe node <node-name> | grep -A5 Capacity
```


---

# Tool

使用：

```
stress-ng
```


版本：

```
stress-ng 0.15.06
```


stress-ng 用途：

- CPU stress testing
- System workload generation
- Resource saturation testing


---

# Benchmark Script

位置：

```
benchmark/cpu/run_stress_ng.sh
```


內容：

```bash
#!/bin/bash

set -e

CPU_WORKERS=${1:-2}
TIMEOUT=${2:-60}

echo "================================"
echo " CPU Benchmark"
echo "================================"

echo "CPU Workers: ${CPU_WORKERS}"
echo "Duration: ${TIMEOUT}s"

stress-ng \
  --cpu ${CPU_WORKERS} \
  --timeout ${TIMEOUT}s \
  --metrics-brief
```


執行：

```bash
./run_stress_ng.sh 2 60
```


參數：

| Parameter | Meaning |
|---|---|
|2|CPU workers|
|60|Execution duration|


---

# Benchmark Command

實際執行：

```bash
stress-ng --cpu 2 --timeout 60s --metrics-brief
```


## --cpu 2

建立兩個 CPU worker。


因為目前 Node：

```
CPU Capacity = 2 cores
```


所以目標：

讓 Node CPU 接近 saturation。


---

## --timeout 60s

Benchmark 執行時間：

```
60 seconds
```


固定時間方便比較不同測試結果。


---

## --metrics-brief

輸出簡化 benchmark metrics。


---

# Result


## Before Benchmark

Node:

```
CPU:
422m

CPU:
21%
```


代表：

```
0.422 / 2 cores
```

約 21% CPU 使用率。


---

## During Benchmark

Node:

```
CPU:
2000m

CPU:
103%
```


2000m:

代表：

```
2 CPU cores
```


CPU 已達 Node capacity。


103% 屬於 metrics-server sampling variation。


---

# stress-ng Result


Example:

```
stressor       bogo ops  real time

cpu             92486     60.00 sec
```


## Bogo Ops

stress-ng 自定義 workload throughput。

用途：

比較不同 CPU configuration 的相對效能。


---

## Real Time

實際測試時間。


---

## CPU Time

所有 CPU worker 累積 CPU 使用時間。


例如：

60 秒測試：

```
4 workers

↓

累積 CPU time 可能 > 60 秒
```

因為多核心同時運算。


---

# Observation


## 1. Pod CPU 來源

Pod 沒有自己的 CPU。


架構：

```text
Node VM CPU

        ↓

Container

        ↓

Pod

        ↓

Process
```


Pod 使用的是 Node 提供的 CPU。


---

## 2. CPU limit 不等於實體 CPU


例如：

```yaml
resources:
  limits:
    cpu: "4"
```


意思：

Container 最多允許使用 4 CPU。


不是：

建立 4 顆 CPU。


如果 Node:

```
CPU Capacity = 2
```


實際最多仍然只有：

```
2 CPU
```


---

## 3. CPU Saturation 驗證


測試前：

```
CPU 21%
```


測試中：

```
CPU 103%
```


代表：

stress-ng 成功讓 Kubernetes Node CPU 達到 saturation。


---

# Interview Questions


## Q1:

Pod 的 CPU 從哪裡來？


Answer:

Pod 沒有自己的 CPU hardware。

Pod 使用 Kubernetes Node VM 提供的 CPU，
由 Linux scheduler 與 cgroup 控制資源。


---

## Q2:

為什麼 CPU limit 設定 4 cores，
但是實際只能使用 2 cores？


Answer:

CPU limit 是 container 使用上限，
不是增加硬體 CPU。

Node capacity 才是真正可使用的硬體資源。


---

# Completed


Week13 Day7-1 完成：

- 建立 benchmark runner
- 固定 benchmark node
- 安裝 stress-ng
- 建立 CPU benchmark script
- 完成 CPU saturation test
- 完成 Kubernetes CPU resource analysis


---

# Next

Week13 Day7-2:

Storage Benchmark

Tool:

```
fio
```

目標：

分析：

- IOPS
- Throughput
- Latency
```
