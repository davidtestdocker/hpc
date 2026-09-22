<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day2 — 確認 Docker 執行環境

[上一課](<day1-why-docker.md>) · [本週目錄](README.md) · [下一課](<day3-image-container.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Docker CLI 是客戶端，daemon 才建立容器；CLI 能印版本不等於能連 daemon。權限錯誤和 daemon 未啟動需分開，不要靠開放 socket 給所有人解決。

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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day2-install-docker.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 2－安裝 Docker Engine

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day4-dockerfile](day4-dockerfile.md)。

---

## 今日目標

在 Ubuntu VM 安裝 Docker 官方版本（Docker CE），讓平台具備 Container Runtime。

---

# 為什麼不用 Ubuntu Repository？

Ubuntu 提供：

- docker.io

本專案使用：

- Docker CE（Docker Community Edition）

原因：

- 官方維護
- 更新速度較快
- 與官方文件一致
- 支援最新功能

---

# 安裝流程

1. 確認系統沒有安裝舊版 Docker。
2. 安裝必要工具：

- ca-certificates
- curl
- gnupg
- lsb-release

3. 加入 Docker 官方 GPG Key。
4. 加入 Docker Official Repository。
5. 更新 Repository。
6. 安裝 Docker CE。

---

# 安裝套件

本次安裝：

- docker-ce
- docker-ce-cli
- containerd.io
- docker-buildx-plugin
- docker-compose-plugin

---

# 驗證

驗證 Docker：

```bash
docker --version
```

輸出：

```
Docker version 29.x.x
```

代表 Docker Engine 與 Docker CLI 可正常使用。

---

驗證 Docker Compose：

```bash
docker compose version
```

輸出：

```
Docker Compose version v5.x.x
```

代表 Docker Compose Plugin 已安裝完成。

---

# 今日重點

Docker Platform 並非只有一個套件，而是由多個元件組成：

- Docker Engine
- Docker CLI
- Container Runtime（containerd）
- Buildx
- Docker Compose

這些元件共同提供完整的 Container Platform。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的服務都將執行於 Docker Container，例如：

- Monitoring Framework
- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

Docker Engine 負責建立與管理這些 Container。

Docker Compose 將負責多個服務的啟動與管理。

---

# 今日成果

平台已具備：

- Docker Engine
- Docker CLI
- Docker Compose

代表 HPC AI Performance Engineering Platform 已完成 Container Runtime 建置，可開始部署 Container。
