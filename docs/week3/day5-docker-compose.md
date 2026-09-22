<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day5 — Compose 與服務連線

[上一課](<day4-dockerfile.md>) · [本週目錄](README.md) · [下一課](<day6-containerize-monitoring.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史配置與概念示例。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

docker compose config 解析／合併設定，本身不建立網路或 container；建立通常發生在 up。現行 Compose 未定義獨立 api-worker，也不能當完整主平台的一鍵重建入口。

## 程式／設定與來源

本次核對：[compose.yaml](<../../compose.yaml>)、[docker/Dockerfile](<../../docker/Dockerfile>)

## 已有結果與解讀

來源：[記錄／示例原文](<day5-docker-compose.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
services:
  monitor:
    image: hpc-monitor:v4
```

這段是舊 Compose 設定，現在 compose.yaml 的服務是 api／redis／postgres，沒有 monitor。ls 結束和 tail 長駐是主程序生命週期示例，不是現行三服務的驗收。

**仍缺的證據／不能證明的事：** 沒有該次 compose config／up 的完整輸出或退出碼；不能把語法檢查當運行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 5－Docker Compose 與 Container 生命週期

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [compose.yaml](../../compose.yaml)：本機服務組合
- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置

---

## 今日目標

理解 Docker Compose 的用途，以及 Container 為什麼會持續執行或停止。

---

# Docker Compose

Docker Compose 用於管理多個相關服務（Services）。

透過 `compose.yaml` 可以描述整個平台需要啟動的 Container。

例如：

```yaml
services:
  monitor:
    image: hpc-monitor:v4
```

Docker Compose 會根據設定建立 Container。

---

# compose.yaml

Compose 描述的是 **Service**，不是 Container。

Container 是 Service 啟動後產生的執行實體。

---

# docker compose config

```bash
docker compose config
```

可驗證 compose.yaml 是否正確。

Docker Compose 也會自動建立預設 Network。

---

# docker compose up

```bash
docker compose up
```

作用：

- 建立 Network
- 建立 Container
- 啟動 Container

---

# Main Process

Container 的生命週期由 Main Process 決定。

例如：

```dockerfile
CMD ["ls","/app"]
```

流程：

```
ls

↓

執行完成

↓

Container 停止
```

---

改為：

```dockerfile
CMD ["tail","-f","/dev/null"]
```

流程：

```
tail

↓

持續等待

↓

Container 持續執行
```

---

# Docker Compose 與 Docker Run

docker run：

適合啟動單一 Container。

docker compose：

適合管理多個服務。

未來平台中的：

- FastAPI
- Monitoring
- Prometheus
- Grafana

都會透過 Compose 管理。

---

# 與 HPC AI Performance Engineering Platform 的關聯

目前平台：

```
Dockerfile
        │
        ▼
Image
        │
        ▼
Compose
        │
        ▼
Container
```

後續將加入：

- FastAPI
- Monitoring Framework
- Prometheus
- Grafana

共同組成完整平台。

---

# 今日重點

- Docker Compose 管理的是 Service。
- Compose 會建立 Container 與 Network。
- Container 的生命週期由 Main Process 決定。
- Main Process 持續執行，Container 就會持續 Running。
- Main Process 結束，Container 就會停止。
