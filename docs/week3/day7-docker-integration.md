<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day7 — Docker 到平台部署

[上一課](<day6-containerize-monitoring.md>) · [本週目錄](README.md) · [下一週](../week4/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：跨課歷史整合摘要。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

「同 image 不同環境結果一致」是過度保證：host kernel、CPU/GPU、driver、資源限制、外部依賴和輸入仍影響結果。文內擴展 monitor／prometheus／grafana／benchmark-worker 的 Compose 區塊是未實作規劃，不是目前 service 清單。

## 程式／設定與來源

本次核對：[compose.yaml](<../../compose.yaml>)、[docker/Dockerfile](<../../docker/Dockerfile>)、[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day6-containerize-monitoring.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PID COMMAND
1   python3
7   ps
```

本課的 hpc-monitor:v5 整合成果回指 Week3 Day6 的這份文內输出；不是另一筆 Day7 獨立驗收。API／Redis／Postgres 的現行 Compose 與該次 monitor 設定要分開讀。

**仍缺的證據／不能證明的事：** 舊文未記錄此執行的精確日期、映像 digest 或独立原始 log；只能稱為舊教材保存的容器輸出，不能稱本次重跑或最新映像驗收。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 7－Docker Integration

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [compose.yaml](../../compose.yaml)：本機服務組合
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

整合 Week 3 Docker 學到的內容，確認 Docker 已經能支撐後續 FastAPI、Monitoring、Benchmark Worker、Prometheus、Grafana 等平台元件。

---

# Week 3 完整流程

本週建立了完整 Docker 工作流程：

```
Source Code
        │
        ▼
Dockerfile
        │
        ▼
docker build
        │
        ▼
Docker Image
        │
        ▼
docker compose
        │
        ▼
Container
        │
        ▼
Main Process
```

---

# 目前平台中的 Docker 元件

目前專案已包含：

```
docker/
└── Dockerfile

compose.yaml

monitoring/
└── process_monitor.py
```

目前已建立 Image：

```
hpc-monitor:v5
```

並可透過 Docker Compose 啟動 Monitoring Container。

---

# Dockerfile 的角色

Dockerfile 是 Image 的規格。

目前 Dockerfile 負責：

- 選擇 Base Image
- 安裝 Python
- 複製 Monitoring 程式
- 指定 Container 啟動時的 Main Process

---

# Image 的角色

Image 是 Container 的模板。

目前：

```
hpc-monitor:v5
```

是本專案第一個自製 Image。

它包含：

- Ubuntu Base
- Python
- monitoring/process_monitor.py

---

# Compose 的角色

Docker Compose 負責描述與啟動服務。

目前：

```yaml
services:
  monitor:
    image: hpc-monitor:v5
```

代表平台有一個 Monitoring Service。

未來會擴展為：

```yaml
services:
  api:
  monitor:
  prometheus:
  grafana:
  benchmark-worker:
```

---

# Main Process

Container 的生命週期由 Main Process 決定。

例如：

```dockerfile
CMD ["python3","/app/monitoring/process_monitor.py"]
```

代表 Container 啟動後會執行 Monitoring 程式。

如果程式結束，Container 也會結束。

---

# 與直接在 Ubuntu 執行的差異

如果直接在 Ubuntu 執行：

```bash
python3 monitoring/process_monitor.py
```

會依賴 Host VM 的 Python 與系統環境。

如果使用 Docker：

```
Docker Image
        │
        ▼
Container
```

則環境被打包進 Image。

優點：

- 環境一致
- 部署方式一致
- 相依套件隔離
- 易於擴充
- 易於交給 Kubernetes 管理

---

# 對 HPC AI Performance Engineering Platform 的意義

Docker 讓平台具備：

## 1. Consistency

同一個 Image 在不同環境中執行結果一致。

## 2. Deployability

服務可以透過 Compose 或 Kubernetes 部署。

## 3. Isolation

FastAPI、Monitoring、Prometheus、Grafana、Benchmark Worker 可各自擁有獨立環境。

## 4. Scalability

未來 Benchmark Worker 可以從 1 個 Container 擴展到多個 Container。

---

# Week 3 最終成果

本週完成：

- Docker Engine 安裝
- Docker Image 使用
- Container 生命週期理解
- Dockerfile 建立
- 自製 Image 建立
- Docker Compose 使用
- Monitoring Framework Container 化

目前平台已具備 Container Foundation。

---

# 下一週銜接

Week 4 將開始建立 FastAPI Benchmark API。

Docker 將繼續作為部署基礎：

```
FastAPI
        │
        ▼
Docker Image
        │
        ▼
Docker Compose
        │
        ▼
API Service
```

Week 4 的目標不是學 FastAPI，而是建立 Benchmark Platform 的 API Entry Point。
