<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day5 — Compose 與服務連線

[上一課](<day4-dockerfile.md>) · [本週目錄](README.md) · [下一課](<day6-containerize-monitoring.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Compose 的 redis 名稱能讓同一網路的容器互找，但主機連線可能需映射埠。現有 compose.yaml 是本機範例；未包含完整背景 worker 與 Kueue／JobSet 前置條件。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[compose.yaml](<../../compose.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    # 連接埠設定清單；容器宣告埠號本身不會自動對外公開。
    ports:
      - "8000:8000"
    environment:
      APP_NAME: HPC API Dev
    # Pod 可掛載的儲存來源，例如 Secret、ConfigMap 或 PVC。
    volumes:
      - ./api:/app/api
  redis:
    # 容器映像及標籤，決定執行的檔案系統與程式版本。
    image: redis:7-alpine
    ports:
      - "6379:6379"
    # 覆寫容器入口指令；多行字串中的 Shell 語法由指定的 shell 解讀。
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
  postgres:
    image: postgres:16-alpine
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day5-docker-compose.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
