<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day2 — 函式與參數

[上一課](<day1-python.md>) · [本週目錄](README.md) · [下一課](<day3-return.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

函式把一件工作封裝成可重複呼叫的步驟。傳入不同 job_id，renderer 應產生不同資源名稱；輸入、輸出與外部副作用要分開看，讀函式不用先讀全部專案。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[api/workloads/renderer.py](<../../api/workloads/renderer.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def render_mpi_jobset(job_id: str) -> str:
    jobset_name = f"mpi-{job_id}".lower()

    template = TEMPLATE_PATH.read_text()

    if PLACEHOLDER not in template:
        raise ValueError(f"Missing placeholder: {PLACEHOLDER}")

    # 字串 replace 替換所有占位符，讓 JobSet 名稱及 worker DNS 使用同一個識別碼。
    return template.replace(PLACEHOLDER, jobset_name)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day2-function.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 2－Function（函式）

## 對應檔案

文中的 `system_monitor.py` 為規劃中的整合模組，目前沒有可連結的實作。

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解 Function 的用途，以及為什麼 Monitoring Framework 必須使用 Function 來設計程式。

---

# 為什麼需要 Function？

如果沒有 Function，相同的程式碼需要一直複製。

例如：

```python
print("Collect Process")
print("Collect Process")
print("Collect Process")
```

當程式越來越大，維護會變得非常困難。

Function 可以將一段程式命名，之後重複呼叫。

---

# Function

建立 Function：

```python
def collect_process():
    print("Collect Process")
```

代表：

建立一個名為 `collect_process` 的功能。

此時 Function 尚未執行。

---

# 呼叫 Function

程式：

```python
collect_process()
```

代表：

呼叫 `collect_process`。

Python Interpreter 會跳到 Function 內部執行程式。

---

# 執行流程

程式：

```python
def collect_process():
    print("Collect Process")

collect_process()
```

執行順序：

1. 建立 Function。
2. 繼續往下執行。
3. 呼叫 Function。
4. 執行 Function 內容。
5. Function 結束。
6. 程式結束。

Function 不會在定義時立即執行。

---

# 今日重點

- Function 是一段有名字、可以重複使用的程式。
- `def` 用來建立 Function。
- 建立 Function 不代表執行。
- 只有呼叫 Function 時才會真正執行。
- 一個 Function 應只負責一件事情。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來 Monitoring Framework 將由許多 Function 組成，例如：

```text
get_processes()

get_cpu_usage()

get_memory_usage()

get_disk_usage()
```

每個 Function 只負責收集一種資訊。

最後由 `system_monitor.py` 統一呼叫，完成整體系統監控。

這種設計可以提升：

- 可讀性
- 可維護性
- 可測試性
- 可擴充性
