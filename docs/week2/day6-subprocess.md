<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day6 — subprocess

[上一課](<day5-dictionary.md>) · [本週目錄](README.md) · [下一課](<day7-stdout.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

subprocess.run 用參數列表啟動外部命令，capture_output 接住輸出，timeout 限制等待。returncode 非零表示命令未按成功契約結束；不應把認證 stderr 原樣寫進公開證據。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def command(args):
    # 統一由 repo 根目錄執行外部工具，並以 timeout 避免認證或 API server 卡住。
    try:
        result = subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"{args[0]} unavailable or timed out") from exc
    if result.returncode:
        # Avoid putting credential-plugin stderr into saved evidence.
        raise RuntimeError(f"command failed (exit {result.returncode}): {' '.join(args)}")
    return result.stdout


def render():
    # 只渲染 Kustomize／Helm，不會套用任何資源到叢集。
    return command([
        "kubectl", "kustomize", "kustomize/overlays/gpu-sg-platform",
        "--enable-helm", "--load-restrictor", "LoadRestrictionsNone",
    ])


def ready_nodes(nodes, pool, gpu=False):
    # Ready 還不夠：節點也必須可排程；GPU 檢查另外要求公布 NVIDIA 資源。
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day6-subprocess.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 6－subprocess 執行 Linux 指令

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

理解 Python 如何透過 `subprocess` 執行 Linux 指令，開始將 Python 與 Linux 系統資訊連接起來。

---

# 為什麼需要 subprocess？

Monitoring Framework 不能依賴人工輸入指令。

例如：

```bash
ps -eo pid,comm
```

這個指令可以列出目前 Linux 上的 Process。

但是平台需要自動執行這些指令，並將結果提供給後續分析使用。

因此需要 Python 主動執行 Linux 指令。

---

# subprocess

`subprocess` 是 Python 用來建立新 Process 並執行外部指令的模組。

例如：

```python
import subprocess

subprocess.run(["ps", "-eo", "pid,comm"])
```

這段程式會讓 Python 執行：

```bash
ps -eo pid,comm
```

---

# 執行流程

```text
Python Process
        │
        ▼
subprocess
        │
        ▼
建立新的 Process
        │
        ▼
執行 ps
        │
        ▼
輸出 Linux Process List
```

---

# 今日實作

程式：

```python
import subprocess

subprocess.run(["ps", "-eo", "pid,comm"])
```

執行：

```bash
python3 monitoring/process_monitor.py
```

可以看到與手動執行以下指令相同的結果：

```bash
ps -eo pid,comm
```

---

# 今日重點

- Python 可以透過 `subprocess` 執行 Linux 指令。
- `subprocess.run()` 會建立新的 Process。
- 目前 `ps` 的輸出仍然只是顯示在終端機。
- 下一步需要將輸出存進 Python 變數，才能提供 Analysis Engine 使用。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Monitoring Framework 的目標是自動收集系統資料。

流程會從：

```text
Linux
        │
        ▼
ps / top / free / iostat
        │
        ▼
Python subprocess
        │
        ▼
Python Data Structure
        │
        ▼
Analysis Engine
        │
        ▼
Performance Report
```

今天完成的是第一步：

```text
Python 可以主動執行 Linux 指令
```

這是後續自動化 Process Monitoring、CPU Monitoring、Memory Monitoring 的基礎。
