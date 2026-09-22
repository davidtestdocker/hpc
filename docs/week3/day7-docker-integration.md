<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day7 — Docker 到平台部署

[上一課](<day6-containerize-monitoring.md>) · [本週目錄](README.md) · [下一週](../week4/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

建置成功證明可產生映像，不證明 API 能連 DB、worker 有 RBAC 或 MPI 成功。部署需要把 image、環境設定、儲存與權限一起配好，再分層驗收。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[kustomize/overlays/gpu-sg-platform/api-values.yaml](<../../kustomize/overlays/gpu-sg-platform/api-values.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
image:
  tag: automatic-worker-20260922-v1
worker:
  enabled: true
service:
  type: ClusterIP
  port: 8000
  targetPort: 8000
ingress:
  enabled: false
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day7-docker-integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
