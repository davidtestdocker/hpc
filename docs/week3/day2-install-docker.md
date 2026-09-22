<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day2 — 確認 Docker 執行環境

[上一課](<day1-why-docker.md>) · [本週目錄](README.md) · [下一課](<day3-image-container.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：版本佔位示例，非驗收。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

docker --version 主要確認 CLI 版本，不證明能連 daemon；compose version 也不證明服務部署成功。現行 Dockerfile 是映像設定，不能補當時 host 的安裝證據。此課不再被列作精確版本驗收。

## 程式／設定與來源

本次核對：[docker/Dockerfile](<../../docker/Dockerfile>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-install-docker.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Docker version 29.x.x
```

29.x.x 和同頁 Compose v5.x.x 都是佔位版本，不是可追溯的完整版本輸出。不能據此認定該版 Docker Engine 與 daemon 均正常。

**仍缺的證據／不能證明的事：** 缺完整版本號、日期、host 資訊、daemon 連線／容器驗收 log；沒有證據就保持缺證，不要求使用者重裝。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
