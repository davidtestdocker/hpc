<!-- current-curriculum: 2026-09-22 -->
# Week15 Day3 — vLLM inference

[上一課](<Day2-PyTorch-Training-Runtime.md>) · [本週目錄](README.md) · [下一課](<Day4-Runtime-Abstraction.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「vLLM inference」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

TTFT 衡量第一個 token 等待，TPOT 描述後續 token 時間，總吞吐還受併發與長度影響。vLLM 是獨立歷史推論案例，模型與環境不同時不能直接跟訓練 byte tokens/s 比較。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[runtime/vllm/runtime.py](<../../runtime/vllm/runtime.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
# class 定義 VLLMRuntime 類別；括號內是繼承的父類別。
class VLLMRuntime(Runtime):
    # 建構子：建立實例時初始化狀態；self 代表此物件本身。
    def __init__(self, endpoint):
        # Store the vLLM server endpoint without a trailing slash
        # rstrip 移除網址尾端的斜線，避免組合 API 路徑時出現雙斜線。
        self.endpoint = endpoint.rstrip("/")

    # 呼叫 /v1/models 確認既有 vLLM 服務可連線。
    def initialize(self):
        # Use the models endpoint to verify that the vLLM server is reachable
        url = f"{self.endpoint}/v1/models"

        # Send an HTTP GET request to the vLLM server
        # with 管理 HTTP 回應的生命週期；離開區塊時關閉回應，timeout 以秒為單位。
        with urllib.request.urlopen(url, timeout=5) as response:
            # Treat any non-200 response as runtime initialization failure
            if response.status != 200:
                raise RuntimeError("vLLM runtime is not available")

    # 定義 run 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def run(self, request):
        # Build the OpenAI-compatible chat completion endpoint
        url = f"{self.endpoint}/v1/chat/completions"
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 VLLMRuntime 如何送 request／解析結果，再到 evidence index 找固定 c16／c32／c64 資料；列出比較時必须固定的 prompt 與輸出長度。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '9,32p' 'runtime/vllm/runtime.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day3-vLLM-Inference-Runtime.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
