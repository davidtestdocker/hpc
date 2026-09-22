<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day4 — Dockerfile 與 build context

[上一課](<day3-image-container.md>) · [本週目錄](README.md) · [下一課](<day5-docker-compose.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史檔案／layer 敘述。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

不能把目前 python:3.12-slim／Uvicorn Dockerfile 說成當時 hpc-monitor:v2 的建置內容。COPY 可讀範圍受 build context 與 .dockerignore 影響；檔案在 repo 不代表必定進入 image。

## 程式／設定與來源

本次核對：[docker/Dockerfile](<../../docker/Dockerfile>)、[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day4-dockerfile.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
/app/monitoring/process_monitor.py
```

原文以此路徑表示監控程式已打包；當時使用 Ubuntu 基底／hpc-monitor:v2，沒有保存完整 docker history 或容器列檔輸出。現行 Dockerfile 的 COPY monitoring 仍存在，但預設啟動 API。

**仍缺的證據／不能證明的事：** 缺舊 image digest、完整 layer 表及列檔 log；原文路徑是文內記載，非独立 artifact。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
