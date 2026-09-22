<!-- readable-curriculum: 2026-09-22 -->
# Week14 Day6 — Dashboard 與實驗驗證

[上一課](<Day5-GPU-Metrics-Monitoring-integration.md>) · [本週目錄](README.md) · [下一週](../week15/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史P100 dashboard觀察。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

repo沒有gpu_stress.cu，不能說已保存可重現的stress程式；custom-dashboard.json未提供本課完整GPU面板。util100%不等於峰值FLOPS或所有硬體單元飽和。

## 程式／設定與來源

本次核對：本課沒有對應獨立程式；依文內命令及觀察核對，不硬接其他元件。

## 已有結果與解讀

來源：[記錄／示例原文](<Day6-gpu-dashboard-establish-and-gpuworkload-verification.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
| GPU Temperature | 約 60°C |
```

文內util0→100%、temp51→60°C是舊觀察，缺原始時間序列與dashboard匯出，不能用現在L4結果冒充。

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

# Week14 Day6：GPU Dashboard 建立與 GPU Workload 驗證

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/k8s/dcgm-exporter-remote.yaml](../../benchmark/k8s/dcgm-exporter-remote.yaml)
- [helm/grafana-10.5.15/grafana/dashboards/custom-dashboard.json](../../helm/grafana-10.5.15/grafana/dashboards/custom-dashboard.json)
- [helm/prometheus/templates/configmap.yaml](../../helm/prometheus/templates/configmap.yaml)

---

## 今日目標

今天將 GPU Metrics 建立為 Grafana Dashboard，並透過實際 GPU Workload 驗證 Dashboard 是否能即時反映 GPU 狀態。

今日流程：

```text
GPU Workload
      │
      ▼
Tesla P100
      │
      ▼
DCGM Exporter
      │
      ▼
Prometheus
      │
      ▼
Grafana Dashboard
```

---

## 1. 建立 GPU Dashboard

Grafana：

```text
Dashboards
    ↓
New Dashboard
    ↓
Add Visualization
```

Data Source：

```text
Prometheus
```

---

## 2. GPU Utilization Panel

Title：

```text
GPU Utilization
```

PromQL：

```promql
DCGM_FI_DEV_GPU_UTIL
```

Unit：

```text
Percent (0-100)
```

用途：

```text
顯示 GPU 使用率 (%)
```

---

## 3. GPU Temperature Panel

Title：

```text
GPU Temperature
```

PromQL：

```promql
DCGM_FI_DEV_GPU_TEMP
```

Unit：

```text
Celsius (°C)
```

用途：

```text
監控 GPU 即時溫度。
```

---

## 4. GPU Power Panel

Title：

```text
GPU Power
```

PromQL：

```promql
DCGM_FI_DEV_POWER_USAGE
```

Unit：

```text
Watts (W)
```

用途：

```text
監控 GPU 即時功耗。
```

---

## 5. VRAM Used Panel

Title：

```text
VRAM Used
```

PromQL：

```promql
DCGM_FI_DEV_FB_USED
```

Unit：

```text
Mebibytes (MiB)
```

用途：

```text
監控目前已使用 GPU Memory。
```

---

## 6. VRAM Free Panel

Title：

```text
VRAM Free
```

PromQL：

```promql
DCGM_FI_DEV_FB_FREE
```

Unit：

```text
Mebibytes (MiB)
```

用途：

```text
監控剩餘 GPU Memory。
```

---

## 7. VRAM Total Panel

Title：

```text
VRAM Total
```

PromQL：

```promql
DCGM_FI_DEV_FB_TOTAL
```

Unit：

```text
Mebibytes (MiB)
```

用途：

```text
顯示 GPU 總記憶體容量。
```

---

## 8. GPU Stress Program

建立：

```text
gpu_stress.cu
```

編譯：

```bash
nvcc gpu_stress.cu -o gpu_stress
```

執行：

```bash
./gpu_stress
```

停止：

```text
Ctrl + C
```

GPU Stress 持續對 GPU 執行 CUDA Kernel，以產生穩定 GPU Workload。

---

## 9. Dashboard 驗證

GPU Workload 執行前：

| Metric | 狀態 |
|------|------|
| GPU Utilization | 約 0% |
| GPU Temperature | 約 51°C |
| VRAM Used | 0 MiB |
| VRAM Free | 約 16270 MiB |

GPU Workload 執行後：

| Metric | 狀態 |
|------|------|
| GPU Utilization | 約 100% |
| GPU Temperature | 約 60°C |
| VRAM Used | 約 256 MiB |
| VRAM Free | 約 16000 MiB |

代表 Dashboard 能即時反映 GPU 狀態變化。

---

## 10. GPU Monitoring 驗證

驗證 GPU Workload 對監控指標的影響：

```text
GPU Workload
        │
        ▼
GPU Utilization ↑
GPU Temperature ↑
GPU Power ↑
VRAM Used ↑
VRAM Free ↓
```

Grafana Dashboard 可即時顯示 GPU 工作負載的變化。

---

## 11. Day6 架構

```text
GPU Stress Program
        │
        ▼
Tesla P100-PCIE-16GB
        │
        ▼
CUDA Runtime
        │
        ▼
NVIDIA Driver
        │
        ▼
nv-hostengine
        │
        ▼
DCGM Exporter
        │
        ▼
Prometheus
        │
        ▼
Grafana Dashboard
```

---

## Day6 完成結果

完成 GPU Dashboard 建立，並成功透過 GPU Workload 驗證：

- GPU Utilization
- GPU Temperature
- GPU Power
- VRAM Used
- VRAM Free
- VRAM Total

所有 GPU Metrics 均能由 Grafana 即時監控，完成 GPU Observability Dashboard 驗證。
