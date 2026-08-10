# Week13 Day7-1 - CPU Benchmark

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
