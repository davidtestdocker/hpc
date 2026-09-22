<!-- readable-curriculum: 2026-09-22 -->
# Week14 Day6 — Dashboard 與實驗驗證

[上一課](<Day5-GPU-Metrics-Monitoring-integration.md>) · [本週目錄](README.md) · [下一週](../week15/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

圖表能輔助看趨勢，但控制條件、raw result 和 trace 才支撐具體性能結論。9/22 取樣包含 setup／warmup／profile，不應直接對整段算平均後當每組 batch 指標。

## 在現在的專案中

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

本課對照：[docs/performance/causal-lm-l4-20260922.md](<../performance/causal-lm-l4-20260922.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
## 限制

單張 L4 採 time-sharing；本次請求一個 share，不保證硬體隔離。啟動前 `nvidia-smi`
沒有其他 compute process，仍不能把共享設定描述為獨占 GPU。telemetry 是低頻採樣，
包含 setup／warmup／profile／trace export，不能把全程平均當作各 batch 的 GPU 使用率。
記憶體數字是 PyTorch peak allocated，與 reserved 或 nvidia-smi memory used 不同。

這是 13M 小型語言模型的受控訓練實驗，無 held-out dataset、生成品質、pretrained
LLM、multi-GPU scaling 或 RDMA 結論；也尚未接入 MPI API 的 benchmark dispatcher。
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
