<!-- readable-curriculum: 2026-09-22 -->
# Week1 Day2 — CPU 排程

[上一課](<day1-linux-process.md>) · [本週目錄](README.md) · [下一課](<day3-context-switch.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

Linux 排程器分配 CPU 執行時間；Kubernetes Scheduler 選擇 Pod 放哪台 node，兩者不是同一層。CPU requests 是排程容量宣告，limits 則可能造成執行時節流。

## 在現在的專案中

本週在自己的 Linux 學習環境做唯讀觀察，不聲稱主叢集當下健康。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week1/day2-cpu-scheduler.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 程序與資源觀察仍是基礎；歷史量測不代表現行服務健康。
> **閱讀順序**：先學本文基礎，再讀[Week1 現行對照與檢核](../learning-guide.md#week1)及[對應現行入口](../runbooks/ai-hpc-job-troubleshooting.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 1 Day 2－CPU Scheduler（CPU 排程器）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[Day1-Linux-CPU-Performance-Analysis](../week12/Day1-Linux-CPU-Performance-Analysis.md)。

---

## 今日目標

理解 Linux Scheduler 如何將 Process 分配到 CPU Core 執行，以及 CPU Core 與 Process 的關係。

---

# 為什麼需要 Scheduler？

CPU Core 的數量有限，但系統中可能同時存在數百個 Process。

Linux Scheduler 的工作就是：

- 決定哪個 Process 先執行
- 決定 Process 執行多久
- 決定下一個要執行哪個 Process

CPU Core 不會自己挑選 Process，而是由 Scheduler 負責分配。

---

# CPU Core 與 Process

目前實驗環境：

- GCP Ubuntu VM
- CPU Core：4

如果同時只有四個 Process：

```
Core0 → Process A
Core1 → Process B
Core2 → Process C
Core3 → Process D
```

每個 Process 都可以直接使用一個 CPU Core。

---

# 實驗一：查看 CPU Core

使用指令：

```bash
nproc
```

輸出：

```
4
```

代表目前 VM 有四個 CPU Core。

---

# 實驗二：建立高 CPU 使用率 Process

執行：

```bash
yes > /dev/null
```

再使用：

```bash
top
```

觀察到：

- 新增一個 Running Process
- `yes` 的 CPU 使用率接近 100%

代表一個 Process 可以吃滿一個 CPU Core。

---

# 實驗三：同時執行兩個 yes

再次執行：

```bash
yes > /dev/null
```

再次觀察 `top`：

可以看到兩個 `yes` Process。

兩個 Process 都接近 100% CPU。

代表 Linux Scheduler 將兩個 Process 分配到不同 CPU Core 執行。

---

# 今日重點

Scheduler 負責將 Process 分配到 CPU Core。

CPU Core 不會自己選擇要執行哪個 Process。

當 CPU Core 足夠時，每個高負載 Process 可以獨占一個 Core。

當 Process 數量超過 CPU Core 數量時，Scheduler 就必須在 Process 之間不停切換。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

本質上都是 Linux Process。

Performance Engineer 必須了解 Scheduler 如何分配 CPU，才能分析：

- CPU 是否成為瓶頸
- Benchmark Worker 是否取得足夠 CPU 資源
- TPS 為何下降
- 是否需要調整 CPU 資源配置
