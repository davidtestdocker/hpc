<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day6 — 監控程式容器化

[上一課](<day5-docker-compose.md>) · [本週目錄](README.md) · [下一課](<day7-docker-integration.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史教材保存的容器輸出。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

現行 Dockerfile 用 Python slim 並啟動 Uvicorn；Compose 已沒有 monitor service。monitor 程式一次列舉後結束，並非長駐監控 daemon。現行 Dockerfile 沒有顯式安裝 ps 所需套件，不能未查 image 就保證預設容器可跑此程式。PID 1／7 是當時容器值，不是固定值。

## 程式／設定與來源

本次核對：[compose.yaml](<../../compose.yaml>)、[docker/Dockerfile](<../../docker/Dockerfile>)、[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<day6-containerize-monitoring.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
PID COMMAND
1   python3
7   ps
```

原文直接記載 hpc-monitor:v5／monitor service 的 docker compose up 輸出。它支持「教材記錄了容器內 Python 呼叫 ps 的結果」，不能升級成已核對映像內容和 raw log 的新驗收。

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

# Week 3 Day 6－Container 化 Monitoring Framework

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [compose.yaml](../../compose.yaml)：本機服務組合
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

將 `monitoring/process_monitor.py` 打包進 Docker Image，並透過 Docker Compose 在 Container 中執行。

---

# Dockerfile

本日 Dockerfile：

```dockerfile
FROM ubuntu:24.04

RUN apt update

RUN apt install -y python3

COPY monitoring /app/monitoring

CMD ["python3","/app/monitoring/process_monitor.py"]
```

---

# RUN

`RUN` 在 Build 階段執行。

例如：

```dockerfile
RUN apt install -y python3
```

代表在建立 Image 時安裝 Python。

安裝結果會保留在 Image 中。

---

# CMD

`CMD` 在 Container 啟動時執行。

例如：

```dockerfile
CMD ["python3","/app/monitoring/process_monitor.py"]
```

代表 Container 啟動後，主程序為：

```text
python3 /app/monitoring/process_monitor.py
```

---

# Build Image

```bash
docker build -f docker/Dockerfile -t hpc-monitor:v5 .
```

Image 由原本約 117MB 增加至約 273MB。

原因是 Image 中安裝了 Python。

---

# Docker Compose

`compose.yaml` 指向：

```yaml
services:
  monitor:
    image: hpc-monitor:v5
```

啟動：

```bash
docker compose up
```

輸出：

```text
PID COMMAND
1   python3
7   ps
```

代表 `process_monitor.py` 已在 Container 內成功執行。

---

# 重要觀察：Container Namespace

Container 中執行 `ps` 時，只會看到 Container 內部 Process。

因此本次看到：

```text
1 python3
7 ps
```

而不是 Host VM 上所有 Process。

這代表 Container 有自己的 Process Namespace。

---

# 今日重點

- `RUN` 用於 Build 階段，結果保留在 Image。
- `CMD` 用於 Container 啟動階段，決定 Main Process。
- Monitoring Framework 已成功在 Container 中執行。
- Container 預設只能看到自己的 Process，不會看到 Host 全部 Process。

---

# 與 HPC AI Performance Engineering Platform 的關聯

本日完成第一個真正容器化的元件：

```text
Monitoring Framework
        │
        ▼
Docker Image
        │
        ▼
Docker Compose
        │
        ▼
Monitoring Container
```

這是後續 FastAPI、Benchmark Worker、Analysis Engine 容器化的範本。
