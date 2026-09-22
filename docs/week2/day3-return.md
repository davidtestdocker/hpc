<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day3 — return 與例外

[上一課](<day2-function.md>) · [本週目錄](README.md) · [下一課](<day4-list.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

return 把值交給呼叫者並結束函式；沒有 return 的路徑通常得到 None。collector 用 None 表示尚未取得終態，不表示 completed，也不應直接當 failed。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[api/worker.py](<../../api/worker.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        update = main.collect_mpi_jobset(job['result']['jobset_name'])
        if update is None:
            return
        guard()
        main.persist_job_status(job_id, update['status'])
        job.update(update)
        job['finished_at'] = datetime.now(timezone.utc).isoformat()
        guard()
        redis.set(key, json.dumps(job))
    else:
        raise ValueError(f'Unsupported job state: {state}')
    # pipeline 預設使用 MULTI/EXEC，把 queue 清理與 done 標記放在同一 Redis 交易。
    # 此交易不涵蓋上方 PostgreSQL；DB-first 失敗時保留可在下一輪重試的狀態。
    guard()
    with redis.pipeline() as pipe:
        pipe.lrem('job_queue', 0, job_id)
        pipe.lrem('processing_queue', 0, job_id)
        if job['status'] == 'failed':
            pipe.lrem('dead_letter_queue', 0, job_id)
            pipe.rpush('dead_letter_queue', job_id)
        if job['status'] in {'completed', 'failed'}:
            pipe.set(f'worker:done:{job_id}', '1')
        pipe.execute()

```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day3-return.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 3－Return（回傳值）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day6-subprocess](day6-subprocess.md)。

---

## 今日目標

理解 Function 如何將資料回傳給其他程式，而不是只輸出到畫面。

---

# print() 與 return 的差異

`print()` 的用途：

- 將資料輸出到終端機
- 方便人閱讀

例如：

```python
print("CPU Usage")
```

畫面會顯示：

```
CPU Usage
```

---

`return` 的用途：

- 將資料回傳給呼叫 Function 的程式
- 提供其他 Function 繼續使用

例如：

```python
def get_cpu():
    return 15
```

並不會輸出任何東西。

只有：

```python
cpu = get_cpu()

print(cpu)
```

才會看到：

```
15
```

---

# 執行流程

程式：

```python
def collect_process():
    return "Collect Process"

result = collect_process()

print(result)
```

流程：

```
建立 Function
        │
        ▼
呼叫 Function
        │
        ▼
return 回傳資料
        │
        ▼
result 接收資料
        │
        ▼
print() 輸出資料
```

---

# 今日重點

- `return` 不會將資料印到畫面。
- `return` 是將資料交給其他程式使用。
- `print()` 是給人閱讀。
- `return` 是給程式使用。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來 Monitoring Framework：

```python
get_processes()

get_cpu_usage()

get_memory_usage()

get_disk_usage()
```

都會使用 `return` 回傳資料。

Analysis Engine 再接收這些資料進行分析。

平台的資料流如下：

```
Monitor
        │
        ▼
return
        │
        ▼
Analysis Engine
        │
        ▼
Report Generator
```

Monitoring Framework 不直接分析資料，而是負責收集並回傳資料。
