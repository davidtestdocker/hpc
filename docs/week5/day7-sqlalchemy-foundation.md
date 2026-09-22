<!-- current-curriculum: 2026-09-22 -->
# Week5 Day7 — SQLAlchemy Session

[上一課](<day6-postgresql-foundation.md>) · [本週目錄](README.md) · [下一週](../week6/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「SQLAlchemy Session」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

Session 管理一次資料庫互動，不是全域永久連線。add／commit／close 各有用途，finally 確保關閉；pool_pre_ping、connect timeout、statement timeout 分別防不同等待。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[api/database/connection.py](<../../api/database/connection.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
from sqlalchemy import create_engine

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres-service"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "hpc_platform"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "hpc"
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 connection.py 與 create_benchmark 的 try/finally，說明 commit 失敗後為何不能繼續向 Redis 宣稱已接受；勿把 timeout 當自動資料修復。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '5,28p' 'api/database/connection.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week5/day7-sqlalchemy-foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
