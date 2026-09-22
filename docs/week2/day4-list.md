<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day4 — list 與迴圈

[上一課](<day3-return.md>) · [本週目錄](README.md) · [下一課](<day5-dictionary.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

list 保存有順序的多筆值；迴圈可逐一處理，而 append 增加新元素。分析效能時同一 batch 的多次結果是一組樣本，不該只拿最佳一次代替全組。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[analysis/causal_lm_report.py](<../../analysis/causal_lm_report.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        selected = [r for r in runs if r['batch_size'] == batch]
        if len(selected) < 3:
            raise ValueError('At least three runs per batch required')
        throughput = [r['tokens_per_second'] for r in selected]
        if not all(math.isfinite(x) and x > 0 for x in throughput):
            raise ValueError('Throughput must be finite and positive')
        # CV = 樣本標準差／均值，表示重複測量波動；不是信賴區間。
        # peak memory 取三次中的最大值；throughput 與 mean step 則各自取平均。
        groups[str(batch)] = {
            'repetitions': len(selected),
            'mean_tokens_per_second': statistics.fmean(throughput),
            'min_tokens_per_second': min(throughput), 'max_tokens_per_second': max(throughput),
            'throughput_cv_percent': statistics.stdev(throughput) / statistics.fmean(throughput) * 100,
            'mean_step_ms': statistics.fmean(r['mean_step_ms'] for r in selected),
            'max_peak_allocated_mib': max(r['peak_allocated_mib'] for r in selected),
            'initial_loss': [r['initial_loss'] for r in selected],
            'final_loss': [r['final_loss'] for r in selected],
        }
    # throughput 上升可代表收益，但 latency／memory 上升則是同時付出的代價。
    change = {metric: (groups['16'][metric] / groups['8'][metric] - 1) * 100
              for metric in ('mean_tokens_per_second', 'mean_step_ms', 'max_peak_allocated_mib')}
    return {'batches': groups, 'batch8_to_16_change_percent': change}


```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day4-list.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 4－List（串列）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解為什麼 Monitoring Framework 必須使用 List 儲存 Process，而不是使用大量獨立變數。

---

# 為什麼需要 List？

Linux 系統同時會有許多 Process。

例如：

- systemd
- bash
- python3
- sshd
- codex

因此 Monitoring Framework 不可能只回傳一個 Process。

需要一個可以儲存多筆資料的資料結構。

---

# List

建立 List：

```python
processes = [
    "systemd",
    "bash",
    "python3"
]
```

代表：

建立一個包含多個元素的集合。

---

# Element（元素）

每一筆資料都是一個 Element。

例如：

```
systemd
bash
python3
```

都是 List 的 Element。

---

# Index（索引）

List 的位置從 0 開始。

例如：

```python
processes[0]
```

得到：

```
systemd
```

而：

```python
processes[2]
```

得到：

```
python3
```

---

# 今日重點

- Linux 同時存在許多 Process。
- List 可以儲存多筆資料。
- List 的 Index 從 0 開始。
- Monitoring Framework 將使用 List 表示多個 Process。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來：

```python
get_processes()
```

將回傳：

```python
[
    {
        "pid": 1,
        "name": "systemd"
    },
    {
        "pid": 8432,
        "name": "python3"
    }
]
```

之後再加入：

- CPU
- Memory
- Status

等資訊。

List 是 Monitoring Framework 第一個核心資料結構。
