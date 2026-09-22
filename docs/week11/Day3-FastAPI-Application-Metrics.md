<!-- current-curriculum: 2026-09-22 -->
# Week11 Day3 — FastAPI application metrics

[上一課](<Day2-Prometheus-ScrapeJob-Target與PullModel.md>) · [本週目錄](README.md) · [下一課](<Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「FastAPI application metrics」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

Instrumentator 自動記錄 HTTP 請求，但 HTTP latency 不等於非同步 MPI 的 end-to-end latency。只量 POST /benchmark 會主要看提交路徑，而非計算時間。

## 在現在的專案中

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

本課對照：[api/main.py](<../../api/main.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
Instrumentator().instrument(app).expose(app)

# class 定義 BenchmarkRequest 類別；括號內是繼承的父類別。
# 繼承 Pydantic BaseModel，FastAPI 依欄位型別驗證 JSON；simulate_failure 預設為 False。
class BenchmarkRequest(BaseModel):
    benchmark: str
    simulate_failure: bool = False


# 回傳 API 首頁資訊。
# @ 是 decorator：將下方函式註冊為指定 HTTP 方法與路徑的處理函式。
@app.get("/")
def root():
    return {
        "message": "HPC API DEV",
        "status": "running"
    }

# 回傳程序健康狀態；這個端點未檢查所有外部相依服務。
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 找 API Instrumentator 初始化，再比較 POST 回應與 worker 完成時間。若要量整筆工作，列出還需哪些時間戳與關聯資訊。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '48,71p' 'api/main.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week11/Day3-FastAPI-Application-Metrics.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
