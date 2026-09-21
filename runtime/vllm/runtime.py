# vLLM HTTP 用戶端：檢查既有推論服務，送出相容 OpenAI 格式的請求；模型由伺服器載入。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import json
import urllib.request

from runtime.base import Runtime


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

        # Convert the Python dictionary into JSON bytes for the HTTP request body
        # dumps 轉成 JSON 字串，encode 再編碼為 HTTP 請求需要的 UTF-8 位元組。
        payload = json.dumps(request).encode("utf-8")

        # Build an HTTP POST request
        # Request 組合 URL、JSON body、Content-Type 與 POST 方法。
        http_request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Send the inference request to vLLM
        with urllib.request.urlopen(http_request, timeout=60) as response:
            # Decode the JSON response and return it as a Python dictionary
            # read 取得位元組，decode 解碼成文字，loads 再還原 JSON 資料。
            return json.loads(response.read().decode("utf-8"))

    # 回傳 runtime 的名稱、類型或裝置資訊。
    def get_info(self):
        # Return metadata describing this runtime
        return {
            "name": "vllm",
            "type": "llm-inference",
            "gpu_required": True,
            "endpoint": self.endpoint,
        }
