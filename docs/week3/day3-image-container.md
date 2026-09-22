<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day3 — Image 與 container

[上一課](<day2-install-docker.md>) · [本週目錄](README.md) · [下一課](<day4-dockerfile.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

image 不會隨容器內每次修改自動改版；刪除容器可能失去可寫層資料。API 與 worker 共用 image，Helm 的 command 可覆寫 image 預設啟動方式。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
          command: ["python", "-m", "api.worker"]
          envFrom:
            # ConfigMap 提供服務位址與輪詢設定；密碼沿用外部建立的 Secret。
            - configMapRef:
                name: {{ include "api.fullname" . }}-config
            - secretRef:
                name: postgres-secret
          resources:
            # requests 供排程器計算容量，limits 限制容器 CPU／記憶體上限。
            {{- toYaml .Values.worker.resources | nindent 12 }}
{{- end }}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day3-image-container.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
