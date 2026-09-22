<!-- readable-curriculum: 2026-09-22 -->
# Week14 Day3 — GPU 監控架構

[上一課](<day2-kubernetes-gpu-scheduling.md>) · [本週目錄](README.md) · [下一課](<Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：監控架構說明，非執行結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

DCGM不是GPU觀測唯一方法，nvidia-smi也是有效來源；Prometheus可透過discovery抓Pod，不一定只能透過Service。

## 程式／設定與來源

本次核對：[helm/prometheus/templates/configmap.yaml](<../../helm/prometheus/templates/configmap.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<day3-gpu-monitoring-architecture.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
DCGM Exporter
```

本課未保存當日GPU metrics；後續P100與L4結果各有自己的環境，不能回填成此日實測。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行是一張 L4，time-sharing shares 不是多 GPU；舊 P100 監控結果保留原環境歸屬。
> **閱讀順序**：先學本文基礎，再讀[Week14 現行對照與檢核](../learning-guide.md#week14)及[對應現行入口](../evidence/README.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week14 Day3 - GPU Monitoring Architecture

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/k8s/dcgm-exporter.yaml](../../benchmark/k8s/dcgm-exporter.yaml)
- [benchmark/k8s/nvidia-dcgm-exporter-service.yaml](../../benchmark/k8s/nvidia-dcgm-exporter-service.yaml)
- [helm/prometheus/templates/configmap.yaml](../../helm/prometheus/templates/configmap.yaml)

---

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
