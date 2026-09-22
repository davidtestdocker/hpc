<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day3 — Image 與 container

[上一課](<day2-install-docker.md>) · [本週目錄](README.md) · [下一課](<day4-dockerfile.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史流程敘述，缺命令結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Container 可以處於 created／running／exited，不應只把它定義成正在執行。Kubernetes 是否重啟還取決於 restartPolicy 和 controller，不是任意退出都必定無限重啟。主 API 的 CMD 已不是互動 bash。

## 程式／設定與來源

本次核對：[docker/Dockerfile](<../../docker/Dockerfile>)

## 已有結果與解讀

來源：[記錄／示例原文](<day3-image-container.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
docker run -it ubuntu:24.04
```

原文描述用互動 shell 啟動 Ubuntu，再 exit 成為 Exited；但沒有保存 container ID、docker ps -a 或 exit code 的實際输出。此命令是當時做法，不是命令結果。

**仍缺的證據／不能證明的事：** 缺 lifecycle 原始觀察与退出碼，無法核實某個具名 container 的狀態轉換。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 3－Image 與 Container

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置

---

## 今日目標

理解 Docker Image 與 Docker Container 的差異，以及 Container 的生命週期。

---

# Image 是什麼？

Image 是 Docker 的模板（Template）。

例如：

- ubuntu:24.04
- python:3.12
- nginx:latest

Image 本身不能執行，它只是建立 Container 的基礎。

---

# Container 是什麼？

Container 是 Image 的執行實體（Running Instance）。

關係如下：

```
Image
    │
    ▼
Container
```

一個 Image 可以建立多個 Container。

---

# docker pull

```bash
docker pull ubuntu:24.04
```

作用：

- 從 Docker Registry 下載 Image
- 不建立 Container
- 不啟動 Container

---

# docker run

```bash
docker run -it ubuntu:24.04
```

作用：

- 使用 Image 建立新的 Container
- 啟動 Container
- 執行預設主程序（本次為 `/bin/bash`）

---

# docker ps

查看目前執行中的 Container。

停止的 Container 不會顯示。

---

# docker ps -a

查看所有 Container。

包含：

- Running
- Exited

---

# Container 的生命週期

本次實驗：

```
docker pull
        │
        ▼
Image
        │
docker run
        ▼
Running Container
        │
exit
        ▼
Exited Container
```

Container 並沒有被刪除，只是停止執行。

---

# Main Process

Container 的生命週期與主程序（Main Process）綁定。

本次主程序為：

```
/bin/bash
```

當執行：

```bash
exit
```

`/bin/bash` 結束，因此 Container 也停止。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的所有服務，例如：

- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

都會以 Docker Container 執行。

每個服務都有自己的 Main Process。

若 Main Process 結束，Container 就會停止，因此 Kubernetes 會負責監控與重新啟動 Container。

---

# 今日重點

- Image 是模板。
- Container 是 Image 的執行實體。
- `docker pull` 只下載 Image。
- `docker run` 建立並啟動新的 Container。
- `docker ps` 查看執行中的 Container。
- `docker ps -a` 查看所有 Container。
- Container 的生命週期由 Main Process 決定。
