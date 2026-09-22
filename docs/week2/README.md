# Week2 — Python：讀懂平台程式的最小基礎

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week1](../week1/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

若 example-a 的狀態也是 completed，依這段程式推演，結果會是 `['example-a', 'example-b']`；這是概念示例，不是外部服務實測。直接對照輸出即可，不需要你再執行。理解後再看 API 的真實 job dict，不必一開始就背 ORM 或 Redis 語法。

本週閱讀純 Python 小例子與示例輸出即可；不用執行，也不要啟動依賴雲端的 worker。

[本週實作／證據入口](<../../tests/test_platform_preflight.py>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Python 變數與資料型別](<day1-python.md>)
- [Day2：函式與參數](<day2-function.md>)
- [Day3：return 與例外](<day3-return.md>)
- [Day4：list 與迴圈](<day4-list.md>)
- [Day5：dict 與 JSON](<day5-dictionary.md>)
- [Day6：subprocess](<day6-subprocess.md>)
- [Day7：stdout 與結構化結果](<day7-stdout.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
