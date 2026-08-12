# Week14 Day6：GPU Dashboard 建立與 GPU Workload 驗證

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
