<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day1 — 為何容器化

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-install-docker.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

主機上的套件版本不同會讓同一程式行為不同。Image 封裝程式及使用者空間依賴，但 GPU driver、kernel、硬體與外部 DB 仍影響結果，因此只有 image tag 不足以重現實驗。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[docker/Dockerfile](<../../docker/Dockerfile>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
FROM python:3.12-slim

# 設定容器環境變數：停用 .pyc 輸出，並讓 Python 日誌即時輸出。
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 設定後续 RUN／COPY 與啟動程式使用的工作目錄。
WORKDIR /app

# 建置映像時執行 Shell 指令；&& 只在前一指令成功後繼續。
RUN groupadd --system app \
    && useradd --system --gid app app

# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY requirements.txt .

# 建置映像時執行 Shell 指令；&& 只在前一指令成功後繼續。
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY --chown=app:app api ./api
# 從建置 context 複製檔案；--chown 設定檔案擁有者。
COPY --chown=app:app monitoring ./monitoring
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day1-why-docker.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 1－為什麼需要 Docker？

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置

---

## 今日目標

理解 Docker 在 HPC AI Performance Engineering Platform 中存在的目的。

Docker 並不是學習目標，而是平台部署與管理的工具。

---

# 為什麼需要 Docker？

目前平台直接在 Ubuntu 上執行：

```text
Ubuntu

├── Python
├── Monitoring Framework
├── FastAPI（未來）
├── Prometheus（未來）
├── Grafana（未來）
└── Benchmark Worker（未來）
```

所有服務都安裝在同一個作業系統中。

當服務越來越多，就容易出現：

- 套件衝突
- Python 版本衝突
- 升級影響其他服務
- 難以部署
- 難以回滾

---

# Docker 解決什麼問題？

Docker 提供：

**Isolation（隔離）**

每一個服務都有自己的執行環境。

例如：

```text
Ubuntu

├── FastAPI Container
│       Python 3.12
│
├── Prometheus Container
│
├── Grafana Container
│
└── Benchmark Worker Container
```

每個 Container 彼此獨立。

其中一個服務更新，不會影響其他服務。

---

# Image 與 Container

Docker 有兩個重要概念：

Image：

```
Template
```

Container：

```
Running Instance
```

兩者關係類似：

```
Program
        │
        ▼
Process
```

Docker：

```
Image
        │
        ▼
Container
```

Image 可以建立多個 Container。

---

# Docker 在平台中的角色

未來平台：

```
Control Node

├── FastAPI Container
├── Prometheus Container
├── Grafana Container
└── Analysis Engine Container

Compute Node

├── Benchmark Worker Container
├── vLLM Container
├── Node Exporter Container
└── DCGM Exporter Container
```

Docker 是所有平台服務的執行環境。

---

# 今日重點

- Docker 的核心價值是隔離（Isolation）。
- Container 可以避免不同服務互相影響。
- Image 是 Container 的模板。
- Container 是真正執行中的服務。
- Docker 是 Kubernetes 的基礎。

---

# 與 HPC AI Performance Engineering Platform 的關聯

本平台未來所有核心元件都會以 Container 執行，包括：

- Monitoring Framework
- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

Docker 讓每個服務可以：

- 獨立部署
- 獨立升級
- 獨立回滾
- 獨立除錯

降低平台維護成本，提升部署一致性。

---

# 面試重點

如果沒有 Docker：

- 不同服務可能產生版本衝突。
- 升級一個服務可能影響整個系統。
- 測試新版本風險較高。

使用 Docker 後：

- 每個服務擁有自己的執行環境。
- 可以快速建立、測試、刪除 Container。
- 適合大型平台的部署與維護。
