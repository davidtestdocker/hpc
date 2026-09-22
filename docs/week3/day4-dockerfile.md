<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day4 — Dockerfile 與 build context

[上一課](<day3-image-container.md>) · [本週目錄](README.md) · [下一課](<day5-docker-compose.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

FROM 選基底、WORKDIR 設工作目錄、COPY 放檔案、RUN 在建置時執行、CMD 設預設命令。COPY 的來源相對 build context，不一定相對 Dockerfile 目錄。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[docker/Dockerfile](<../../docker/Dockerfile>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
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

# 後續步驟與容器啟動使用此帳號。
USER app

# 宣告程式使用的埠號；仍需 Service 或 port mapping 才能對外連線。
EXPOSE 8000

```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day4-dockerfile.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 4－Dockerfile 與建立自己的 Image

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

學會使用 Dockerfile 建立自己的 Docker Image，而不是只使用官方 Image。

---

# Dockerfile

Dockerfile 是建立 Docker Image 的規格（Specification）。

Docker 會依照 Dockerfile 的內容建立新的 Image。

---

# FROM

```dockerfile
FROM ubuntu:24.04
```

指定 Base Image。

新的 Image 會建立在 ubuntu:24.04 之上。

---

# COPY

```dockerfile
COPY monitoring /app/monitoring
```

將本機的 `monitoring` 目錄複製到 Image 中。

注意：

COPY 發生在 Build 階段，而不是 Run 階段。

---

# docker build

```bash
docker build -f docker/Dockerfile -t hpc-monitor:v2 .
```

作用：

- 讀取 Dockerfile
- 建立新的 Image
- 將 Image 命名為 `hpc-monitor:v2`

---

# Build Context

本次使用：

```bash
.
```

代表 Build Context 為整個專案根目錄。

因此 Dockerfile 可以存取：

- monitoring/
- docker/
- docs/

如果 Context 設定錯誤，COPY 將找不到檔案。

---

# docker history

使用：

```bash
docker history hpc-monitor:v2
```

可以查看 Image 的 Layer。

本次新增：

```
COPY monitoring /app/monitoring
```

代表 Image 新增了一個 Layer。

---

# Image 與 Container

流程如下：

```
Source Code
        │
        ▼
docker build
        │
        ▼
Image
        │
docker run
        ▼
Container
```

Container 中可以看到：

```
/app/monitoring/process_monitor.py
```

代表程式已經被打包進 Image。

---

# 今日重點

- Dockerfile 是 Image 的規格。
- FROM 指定 Base Image。
- COPY 將本機檔案打包進 Image。
- docker build 建立新的 Image。
- docker history 可查看 Image Layer。
- Build 與 Run 是不同階段。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- Monitoring
- FastAPI
- Analysis
- Benchmark Worker

都會有自己的 Dockerfile。

CI/CD 流程：

```
修改程式
        │
        ▼
docker build
        │
        ▼
Image
        │
        ▼
Container
```

這也是 GitHub Actions 自動建置 Image 的基礎。
