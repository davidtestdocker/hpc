# Week2 — Python：讀懂平台程式的最小基礎

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week1](../week1/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

變數是名稱與物件的綁定；str、number、list、dict 用來表達不同資料。縮排定義區塊，條件決定分支，迴圈重複處理多筆資料。

函式接收參數、執行工作，並以 return 交回結果。print 是輸出，不是回傳值。例外會改變控制流程；try/finally 適合確保資源釋放，但不會自動讓失敗的操作成功。

外部命令也是可能失敗的工作。subprocess 要關注參數、timeout、stdout、stderr 和 returncode；不是有文字輸出就算成功。先理解小函式，再追整個 API。

## 目前環境與實測邊界

### 不需要外部服務的最小例子

```python
def summarize(jobs):
    completed = []
    for job in jobs:
        if job["status"] == "completed":
            completed.append(job["job_id"])
    return completed

jobs = [
    {"job_id": "example-a", "status": "accepted"},
    {"job_id": "example-b", "status": "completed"},
]
result = summarize(jobs)
print(result)  # ['example-b']
```

`def` 定義函式，`jobs` 是傳入的參數；外層 `[]` 是 list，內層 `{}` 是 dict。`for` 逐筆取出，`if` 選擇條件成立者，`append` 加入結果，`return` 把結果交還呼叫者，`print` 才把它顯示出來。這裡的 ID 是教學字串，不是實際平台 UUID。

試著將 example-a 的狀態改成 completed，先預測輸出再執行。理解後再看 API 的真實 job dict；不要一開始就背 ORM 或 Redis 語法。

本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

[本週實作／證據入口](<../../tests/test_platform_preflight.py>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Python 變數與資料型別](<day1-python.md>)
- [Day2：函式與參數](<day2-function.md>)
- [Day3：return 與例外](<day3-return.md>)
- [Day4：list 與迴圈](<day4-list.md>)
- [Day5：dict 與 JSON](<day5-dictionary.md>)
- [Day6：subprocess](<day6-subprocess.md>)
- [Day7：stdout 與結構化結果](<day7-stdout.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
