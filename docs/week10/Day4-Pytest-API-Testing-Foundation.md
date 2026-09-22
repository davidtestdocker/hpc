<!-- current-curriculum: 2026-09-22 -->
# Week10 Day4 — pytest 與斷言

[上一課](<Day3-CodeQuality-withRuff.md>) · [本週目錄](README.md) · [下一課](<Day5-Pytest-MockCI-Integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「pytest 與斷言」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

test 用 assert 表達可檢查的契約，fixture 建立條件。只有測到的行為才有保障；一個 HTTP 測試成功不代表 real cluster 跑過。

## 在現在的專案中

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

本課對照：[tests/test_api.py](<../../tests/test_api.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def test_root():
    body = root()

    assert body["message"] == "HPC API DEV"
    assert body["status"] == "running"


# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_benchmarks():
    body = list_benchmarks()

    assert "benchmarks" in body
    assert isinstance(body["benchmarks"], list)
    assert body["benchmarks"] == [
        "cpu",
        "memory",
        "disk_io",
        "mpi",
    ]

# 定義測試案例，以 assert 驗證實際結果符合預期。
def test_submit_benchmark():
    body = create_benchmark(BenchmarkRequest(benchmark="cpu"))

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 tests/test_api.py，找 client、mock、assert，分別說明輸入、外部依賴替身和預期結果。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '7,30p' 'tests/test_api.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../tests/test_worker.py>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week10/Day4-Pytest-API-Testing-Foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
