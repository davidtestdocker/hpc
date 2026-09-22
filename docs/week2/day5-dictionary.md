<!-- readable-curriculum: 2026-09-22 -->
# Week2 Day5 — dict 與 JSON

[上一課](<day4-list.md>) · [本週目錄](README.md) · [下一課](<day6-subprocess.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

dict 用 key 查值，JSON 是交換資料的文字格式。json.dumps 做序列化、json.loads 還原；Redis 保存的 JSON 字串不是 Python 物件本身。

## 在現在的專案中

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
        pipe.set(f"job:{job_id}", json.dumps(job))
        pipe.rpush('job_queue', job_id)
        pipe.execute()
    return {
        "message": "benchmark request received",
        "job_id": job_id,
        "benchmark": request.benchmark,
        "status": "accepted",
        "next_step": f"Check job status at GET /jobs/{job_id}"
    }

#第八週要改成scan而不是keys方式
# 讀取 job:* 對應的工作；KEYS 會掃描鍵空間，資料量大時有阻塞風險。
@app.get("/jobs")
def get_jobs():

    job_keys = redis_client.keys("job:*")

    jobs = []

    for key in job_keys:
        # loads 把 JSON 字串還原成 Python 字典或清單。
        job = json.loads(
            redis_client.get(key)
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week2/day5-dictionary.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：先學函式／資料結構／subprocess，再追現行檢查工具；不必先懂完整叢集。
> **閱讀順序**：先學本文基礎，再讀[Week2 現行對照與檢核](../learning-guide.md#week2)及[對應現行入口](../../scripts/platform.py)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 2 Day 5－Dictionary（字典）

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[day3-job-identity](../week4/day3-job-identity.md)。

---

## 今日目標

理解如何使用 Dictionary 表示一個 Process 的完整資訊，建立 Monitoring Framework 的基本資料模型。

---

# 為什麼需要 Dictionary？

Linux 的一個 Process 不只有名稱。

例如：

```text
PID     COMMAND     RSS
1       systemd     12584
```

一個 Process 至少包含：

- PID
- Name
- Memory

因此需要一個可以描述多個屬性的資料結構。

---

# Dictionary

建立：

```python
process = {
    "pid": 1,
    "name": "systemd",
    "memory": 15
}
```

代表：

一個 Process 的完整資訊。

---

# Key 與 Value

例如：

```python
"pid": 1
```

其中：

- `pid` 是 Key
- `1` 是 Value

Key 表示欄位名稱。

Value 表示實際資料。

---

# List 與 Dictionary 的關係

一個 Process：

```python
{
    "pid": 1,
    "name": "systemd"
}
```

很多 Process：

```python
[
    {
        "pid": 1,
        "name": "systemd"
    },
    {
        "pid": 320,
        "name": "python3"
    }
]
```

List 用來保存很多 Process。

Dictionary 用來表示一個 Process。

---

# 今日重點

- Dictionary 可以描述一筆完整資料。
- Key 表示欄位。
- Value 表示資料。
- Monitoring Framework 會使用 Dictionary 表示一個 Process。
- List 則保存多個 Process。

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
        "name": "systemd",
        "cpu": 0.2,
        "memory": 15
    }
]
```

Analysis Engine 將依據：

- PID
- CPU
- Memory

分析：

- CPU Bottleneck
- Memory Bottleneck
- Process 使用情況

Dictionary 是 Monitoring Framework 最核心的資料模型之一。
