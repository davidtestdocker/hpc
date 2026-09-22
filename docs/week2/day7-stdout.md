<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day7 — stdout 與結構化結果

[上一課](<day6-subprocess.md>) · [本週目錄](README.md) · [下一週](../week3/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

stdout 是文字通道，可能是 JSON、日誌或空字串；成功判定還要看 exit code 與資料欄位。混入 log 的文字不能直接當 JSON 解析。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[scripts/platform.py](<../../scripts/platform.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def inspect(context, require_gpu=True):
    # 這份盤點只讀 Kubernetes metadata，不讀 Secret data，也不執行 workload。
    checks = []
    base = ["kubectl", "--context", context, "--request-timeout=15s"]

    def check(name, args, predicate=lambda data: True):
        # 單項失敗留在報告中，讓操作者一次看到所有前置條件，而不是遇到第一項就退出。
        try:
            data = json.loads(command(base + args + ["-o", "json"]))
            passed = bool(predicate(data))
            detail = "verified" if passed else "resource exists but readiness condition not met"
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            passed, detail = False, str(exc)
        checks.append({"name": name, "passed": passed, "detail": detail})

    check("system node ready", ["get", "nodes"], lambda d: ready_nodes(d, "system-pool"))
    if require_gpu:
        check("GPU resource advertised", ["get", "nodes"],
              lambda d: ready_nodes(d, "gpu-pool", True))
    check("namespace", ["get", "namespace", NAMESPACE])
    for crd in ["jobsets.jobset.x-k8s.io", "localqueues.kueue.x-k8s.io"]:
        check(crd, ["get", "crd", crd], lambda d: any(
            c["type"] == "Established" and c["status"] == "True"
            for c in d.get("status", {}).get("conditions", [])))
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day7-stdout.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 7－取得 Linux 指令輸出（stdout）

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [monitoring/process_monitor.py](../../monitoring/process_monitor.py)：程序資訊收集

---

## 今日目標

理解 Python 如何取得 Linux 指令的輸出，而不是僅執行指令。

---

# 為什麼需要 stdout？

昨天：

```python
subprocess.run(["ps", "-eo", "pid,comm"])
```

只能執行 Linux 指令。

Process List 直接輸出到終端機。

Python 無法繼續處理這些資料。

---

# stdout（Standard Output）

Linux 指令的正常輸出稱為 Standard Output（stdout）。

例如：

```bash
ps -eo pid,comm
```

輸出的 Process List 就是 stdout。

---

# subprocess

程式：

```python
result = subprocess.run(
    ["ps", "-eo", "pid,comm"],
    capture_output=True,
    text=True
)
```

其中：

- `capture_output=True`：將 stdout 保留給 Python。
- `text=True`：將輸出轉換為 Python 字串。

---

# 取得 stdout

程式：

```python
print(result.stdout)
```

Python 就能取得：

```
PID COMMAND
1 systemd
2 kthreadd
...
```

這些資料。

---

# 執行流程

```
Linux
        │
        ▼
ps
        │
        ▼
stdout
        │
        ▼
Python Variable
        │
        ▼
後續分析
```

---

# 今日重點

- Python 不只可以執行 Linux 指令。
- Python 更可以取得 Linux 指令的輸出。
- stdout 是 Monitoring Framework 收集資料的重要來源。
- 後續會將 stdout 解析成 Python 資料結構。

---

# 與 HPC AI Performance Engineering Platform 的關聯

Monitoring Framework 的第一步就是收集 Linux 系統資訊。

流程如下：

```
Linux Command
        │
        ▼
stdout
        │
        ▼
Python
        │
        ▼
List / Dictionary
        │
        ▼
Analysis Engine
        │
        ▼
Performance Report
```

今天完成的是：

Linux 資料正式進入 Python，成為平台可以分析的資料來源。
