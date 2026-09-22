<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day6 — 監控程式容器化

[上一課](<day5-docker-compose.md>) · [本週目錄](README.md) · [下一課](<day7-docker-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

容器看到的 PID／資源視圖受 namespace 與權限影響。容器內監控程序看不到所有 host 程序時，不代表 host 沒有負載；提高權限之前先界定觀測範圍。

## 在現在的專案中

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

本課對照：[monitoring/process_monitor.py](<../../monitoring/process_monitor.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True,
    check=False
)

print(result.stdout)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week3/day6-containerize-monitoring.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
