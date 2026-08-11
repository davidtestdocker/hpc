# Week14 Day3 - GPU Monitoring Architecture

# 今天平台增加了什麼？

本日建立 GPU Monitoring Foundation。

目的不是立即監控 GPU，而是理解 GPU Metrics 如何整合到既有 Prometheus + Grafana Platform。

本日完成：

- nvidia-smi
- DCGM
- DCGM Exporter
- GPU Metrics
- Prometheus Integration
- Grafana Integration
- GPU Monitoring Architecture

---

# Key Takeaways

## 1.

nvidia-smi

是 NVIDIA 官方提供的 GPU 狀態查詢工具。

適合人工查看：

- GPU Utilization
- GPU Memory
- Temperature
- Power
- Driver
- CUDA Version

Prometheus 無法直接讀取 nvidia-smi。

---

## 2.

DCGM

(Data Center GPU Manager)

負責取得 GPU 監控資料。

例如：

- GPU Utilization
- GPU Memory
- Temperature
- Power
- GPU Clock
- PCIe Throughput

DCGM 是 GPU Metrics 的來源。

---

## 3.

DCGM Exporter

負責將 DCGM 資料轉換成 Prometheus Metrics。

Prometheus 不會直接讀取 GPU。

必須透過：

DCGM Exporter。

---

## 4.

DCGM Exporter

通常以：

DaemonSet

部署。

原因：

每個 GPU Node

都需要一個 Exporter。

GPU Node 有幾台，

Exporter 就有幾個 Pod。

---

## 5.

Prometheus

通常透過：

Service

收集 Metrics。

不是直接 Scrape Pod。

因為：

Pod IP

可能改變。

---

## 6.

Grafana

不直接讀 GPU。

Grafana

查詢的是：

Prometheus。

Prometheus

才是 Metrics Database。

---

## 7.

DCGM Exporter

是 GPU Metrics 唯一入口。

若 DCGM Exporter 故障：

Prometheus

將無法收集 GPU Metrics。

Grafana Dashboard

也將停止更新。

---

## 8.

GPU Monitoring

並不是新的監控系統。

而是：

GPU Metrics

整合進：

Prometheus

+

Grafana

形成統一的 Observability Platform。

---

# GPU Monitoring Architecture

```text
                GPU Hardware
                     │
                     ▼
                NVIDIA Driver
                     │
                     ▼
                    DCGM
                     │
                     ▼
              DCGM Exporter
                (DaemonSet)
                     │
                  Service
                     │
                     ▼
               Prometheus
                     │
                     ▼
                 Grafana
```

---

# Component Responsibilities

| Component | Responsibility |
|------------|----------------|
| GPU | 執行 AI 運算 |
| NVIDIA Driver | 控制 GPU |
| DCGM | 收集 GPU Metrics |
| DCGM Exporter | 提供 Prometheus Metrics |
| Service | 提供固定 Metrics 入口 |
| Prometheus | 收集與儲存 Metrics |
| Grafana | Dashboard 與 Visualization |

---

# nvidia-smi vs DCGM Exporter

| nvidia-smi | DCGM Exporter |
|------------|---------------|
| 人工查看 | Prometheus 收集 |
| CLI Tool | Metrics Exporter |
| 即時查詢 | 持續監控 |
| 單機使用 | Kubernetes Cluster |

---

# Deployment Architecture

GPU Metrics：

```text
GPU Node1

↓

DCGM Exporter
```

```text
GPU Node2

↓

DCGM Exporter
```

```text
GPU Node3

↓

DCGM Exporter
```

DaemonSet：

每個 GPU Node

都會部署：

一個 DCGM Exporter。

---

# Monitoring Flow

```text
GPU

↓

DCGM

↓

DCGM Exporter

↓

Service

↓

Prometheus

↓

Grafana
```

---

# Hands-on

目前平台：

尚未建立 GPU Pool。

因此：

Day3

先建立 GPU Monitoring 架構觀念。

Day4

將實際部署：

- NVIDIA Device Plugin
- DCGM Exporter
- GPU Node

並驗證：

GPU Metrics

成功進入：

Prometheus。

---

# Platform Engineering Insight

GPU Monitoring

不是每天執行：

nvidia-smi。

真正 Production：

建立：

DCGM Exporter

↓

Prometheus

↓

Grafana

形成完整 GPU Observability Platform。

CPU 與 GPU

共用同一套 Monitoring Platform。

---

# Interview Questions

## Q1

nvidia-smi 與 DCGM Exporter 差異？

Answer：

nvidia-smi

提供人工查看 GPU 狀態。

DCGM Exporter

提供 Prometheus 收集 GPU Metrics。

---

## Q2

為什麼 DCGM Exporter 使用 DaemonSet？

Answer：

每個 GPU Node

都需要自己的 GPU Metrics Collector。

因此使用 DaemonSet。

---

## Q3

Prometheus 是否直接讀 GPU？

Answer：

不是。

Prometheus

透過：

DCGM Exporter

收集 GPU Metrics。

---

## Q4

Grafana 是否直接讀 GPU？

Answer：

不是。

Grafana

查詢的是：

Prometheus。

---

## Q5

如果 DCGM Exporter 故障會發生什麼？

Answer：

Prometheus

將無法收集 GPU Metrics。

Grafana GPU Dashboard

也將停止更新。

---

# Completed

Week14 Day3 完成：

- GPU Monitoring Architecture
- nvidia-smi
- DCGM
- DCGM Exporter
- DaemonSet
- Prometheus Integration
- Grafana Integration
- GPU Observability Platform

---

# Next

Week14 Day4

Real GPU Platform

- 建立 GPU Node Pool
- 驗證 nvidia.com/gpu
- 部署 NVIDIA Device Plugin（Helm）
- 驗證 nvidia-smi
- 部署 DCGM Exporter（Helm）
- GPU Metrics → Prometheus → Grafana
- 執行第一個 GPU Benchmark Pod
