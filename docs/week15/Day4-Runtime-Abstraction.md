# Week15 Day4 - Runtime Abstraction

## 今日目標

建立 AI Runtime Abstraction，讓平台不再直接綁死單一 Runtime，而是透過統一介面與 Runtime Manager 選擇不同 Backend。

本日完成：

- Runtime Interface
- Runtime Manager
- PyTorch Runtime Adapter
- vLLM Runtime Adapter
- Runtime Switching
- Lazy Import
- Runtime Metadata
- vLLM Runtime 初始化驗證
- vLLM Runtime Inference 驗證

---

# 今日新增平台能力

新增：

```text
Runtime Abstraction Layer
```

平台架構從：

```text
Platform
   ↓
直接呼叫特定 Runtime
```

進化成：

```text
Platform
   ↓
Runtime Manager
   ↓
Runtime Interface
   ↓
Runtime Adapter
   ├── PyTorchRuntime
   └── VLLMRuntime
```

未來可以再擴充：

```text
ONNX Runtime
TensorRT
```

而不需要重新修改上層平台邏輯。

---

# 1. Runtime 是什麼

Runtime 是實際負責執行 AI Workload 的執行環境或引擎。

例如：

```text
PyTorch Runtime
→ Tensor Compute
→ Training
→ General Model Inference
```

vLLM：

```text
vLLM Runtime
→ LLM Inference
→ Request Scheduling
→ Continuous Batching
→ KV Cache
```

兩者用途不同，但平台希望能用統一方式管理。

---

# 2. Interface 是什麼

Interface 是共同規格。

Day4 定義所有 Runtime 都必須提供：

```text
initialize()
run()
get_info()
```

因此：

```text
PyTorchRuntime
VLLMRuntime
```

雖然底層實作完全不同，但都遵守同一套操作方式。

概念：

```text
Runtime Interface
      │
      ├── initialize()
      ├── run()
      └── get_info()
```

---

# 3. Adapter 是什麼

Adapter 是適配層。

不同 Runtime 原本的操作方式不同：

```text
PyTorch
→ torch.cuda
→ tensor
→ model
```

vLLM：

```text
HTTP
→ /v1/models
→ /v1/chat/completions
```

Adapter 將它們包成：

```text
initialize()
run()
get_info()
```

因此上層不需要知道底層細節。

---

# 4. Runtime Interface

新增：

```text
runtime/base.py
```

內容：

```python
from abc import ABC, abstractmethod


class Runtime(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def run(self, request):
        pass

    @abstractmethod
    def get_info(self):
        pass
```

---

# 5. ABC

ABC：

```text
Abstract Base Class
```

中文可以理解為：

```text
抽象基底類別
```

用途是定義所有 Runtime 都必須遵守的共同規格。

---

# 6. abstractmethod

使用：

```python
@abstractmethod
```

代表：

```text
子類別必須實作這個方法
```

因此未來：

```text
PyTorchRuntime
VLLMRuntime
ONNXRuntime
TensorRTRuntime
```

都必須實作：

```text
initialize()
run()
get_info()
```

---

# 7. PyTorch Runtime Adapter

原本 Day1：

```text
runtime/pytorch/runtime.py
```

主要是直接：

```text
檢查 CUDA
↓
建立 Tensor
↓
GPU MatMul
↓
驗證 GPU Runtime
```

Day4 將它改造成：

```text
Runtime Interface
      ↓
PyTorchRuntime
```

---

# 8. PyTorchRuntime

主要結構：

```python
class PyTorchRuntime(Runtime):
    def __init__(self):
        self.torch = None
        self.device = None
        self.gpu_name = None

    def initialize(self):
        import torch

        self.torch = torch

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")

        self.device = torch.device("cuda:0")
        self.gpu_name = torch.cuda.get_device_name(self.device)

    def run(self, request=None):
        if self.torch is None or self.device is None:
            raise RuntimeError("Runtime is not initialized")

        a = self.torch.randn((2048, 2048), device=self.device)
        b = self.torch.randn((2048, 2048), device=self.device)
        c = self.torch.matmul(a, b)

        self.torch.cuda.synchronize()

        return {
            "status": "completed",
            "result_device": str(c.device),
        }

    def get_info(self):
        return {
            "name": "pytorch",
            "type": "compute",
            "gpu_required": True,
            "gpu_name": self.gpu_name,
        }
```

---

# 9. __init__

建立：

```python
runtime = PyTorchRuntime()
```

時：

```python
__init__()
```

會自動執行。

初始狀態：

```text
torch = None
device = None
gpu_name = None
```

直到：

```text
initialize()
```

真正執行時才設定。

---

# 10. self

`self` 代表目前這個 Runtime Object 本身。

例如：

```python
runtime1 = PyTorchRuntime()
runtime2 = PyTorchRuntime()
```

執行：

```python
runtime1.initialize()
```

裡面的：

```python
self
```

就是：

```text
runtime1
```

因此：

```python
self.device = ...
```

就是修改：

```text
runtime1.device
```

---

# 11. Lazy Import

一開始 PyTorchRuntime 在檔案最上方：

```python
import torch
```

這會造成：

```text
Import RuntimeManager
↓
Import PyTorchRuntime
↓
立即 Import torch
↓
Host 沒裝 torch
↓
ModuleNotFoundError
```

因此 Day4 改成：

```python
def initialize(self):
    import torch
```

這種方式稱為：

```text
Lazy Import
```

也就是：

```text
真的要使用 PyTorch Runtime 時
才載入 PyTorch
```

---

# 12. Lazy Import 的好處

現在：

```text
RuntimeManager
```

本身不需要 Host 預先安裝：

```text
PyTorch
```

只有：

```text
get_runtime("pytorch")
↓
initialize()
```

真正要執行 PyTorch Runtime 時才需要 PyTorch Environment。

這讓 Runtime Abstraction 不會被單一 Backend Dependency 綁死。

---

# 13. vLLM Runtime Adapter

新增：

```text
runtime/vllm/runtime.py
```

vLLM 已經在 Day3 建立完成，因此 Day4 不重新實作 vLLM。

只新增 Adapter：

```text
Runtime Interface
      ↓
VLLMRuntime
      ↓
Existing vLLM Server
```

---

# 14. VLLMRuntime

內容：

```python
import json
import urllib.request

from runtime.base import Runtime


class VLLMRuntime(Runtime):
    def __init__(self, endpoint):
        # Store the vLLM server endpoint without a trailing slash
        self.endpoint = endpoint.rstrip("/")

    def initialize(self):
        # Use the models endpoint to verify that the vLLM server is reachable
        url = f"{self.endpoint}/v1/models"

        # Send an HTTP GET request to the vLLM server
        with urllib.request.urlopen(url, timeout=5) as response:
            # Treat any non-200 response as runtime initialization failure
            if response.status != 200:
                raise RuntimeError("vLLM runtime is not available")

    def run(self, request):
        # Build the OpenAI-compatible chat completion endpoint
        url = f"{self.endpoint}/v1/chat/completions"

        # Convert the Python dictionary into JSON bytes for the HTTP request body
        payload = json.dumps(request).encode("utf-8")

        # Build an HTTP POST request
        http_request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Send the inference request to vLLM
        with urllib.request.urlopen(http_request, timeout=60) as response:
            # Decode the JSON response and return it as a Python dictionary
            return json.loads(response.read().decode("utf-8"))

    def get_info(self):
        # Return metadata describing this runtime
        return {
            "name": "vllm",
            "type": "llm-inference",
            "gpu_required": True,
            "endpoint": self.endpoint,
        }
```

---

# 15. Endpoint

Endpoint 就是服務位址。

例如：

```text
http://10.148.0.10:30800
```

Day4 的 VLLMRuntime 不直接操作：

```text
CUDA
PyTorch Tensor
Qwen Model Object
```

而是透過 HTTP 呼叫 Day3 已完成的 vLLM Server。

---

# 16. VLLMRuntime initialize()

執行：

```python
runtime.initialize()
```

實際上會呼叫：

```text
GET /v1/models
```

用途：

```text
確認 vLLM Server 是否可以正常連線
```

流程：

```text
VLLMRuntime
      ↓
initialize()
      ↓
/v1/models
      ↓
HTTP 200
      ↓
Runtime Available
```

---

# 17. VLLMRuntime run()

執行：

```python
runtime.run(request)
```

會將 Request：

```text
Python Dictionary
```

轉成：

```text
JSON
```

再送到：

```text
/v1/chat/completions
```

流程：

```text
RuntimeManager
      ↓
VLLMRuntime
      ↓
run()
      ↓
HTTP POST
      ↓
vLLM Server
      ↓
Qwen
      ↓
NVIDIA L4
      ↓
Generated Response
```

---

# 18. Runtime Manager

新增：

```text
runtime/manager.py
```

內容：

```python
class RuntimeManager:
    def get_runtime(self, name, **kwargs):
        # Create the PyTorch runtime only when it is requested
        if name == "pytorch":
            from runtime.pytorch.runtime import PyTorchRuntime
            return PyTorchRuntime()

        # Create the vLLM runtime only when it is requested
        if name == "vllm":
            from runtime.vllm.runtime import VLLMRuntime
            return VLLMRuntime(**kwargs)

        # Reject runtime names that are not registered
        raise ValueError(f"Unsupported runtime: {name}")
```

---

# 19. Runtime Manager 的責任

RuntimeManager 負責：

```text
Runtime Selection
Runtime Creation
Runtime Registration Logic
```

上層不直接：

```python
PyTorchRuntime()
```

也不直接：

```python
VLLMRuntime(...)
```

而是統一：

```python
manager.get_runtime(...)
```

---

# 20. **kwargs

RuntimeManager 使用：

```python
**kwargs
```

代表可以接收 Runtime-specific 額外參數。

例如：

```python
manager.get_runtime(
    "vllm",
    endpoint="http://10.148.0.10:30800"
)
```

其中：

```text
endpoint
```

會被傳給：

```python
VLLMRuntime(endpoint=...)
```

PyTorch 不需要 endpoint，所以：

```python
manager.get_runtime("pytorch")
```

即可。

---

# 21. Runtime Switching

Day4 最重要的驗證：

```python
from runtime.manager import RuntimeManager

manager = RuntimeManager()

pytorch_runtime = manager.get_runtime("pytorch")

vllm_runtime = manager.get_runtime(
    "vllm",
    endpoint="http://10.148.0.10:30800"
)

print("pytorch ->", type(pytorch_runtime).__name__)
print("vllm    ->", type(vllm_runtime).__name__)
```

結果：

```text
pytorch -> PyTorchRuntime
vllm    -> VLLMRuntime
```

代表：

```text
同一個 RuntimeManager
        │
        ├── pytorch
        │      ↓
        │ PyTorchRuntime
        │
        └── vllm
               ↓
          VLLMRuntime
```

Runtime Switching 成功。

---

# 22. Runtime Metadata

PyTorch：

```python
runtime.get_info()
```

概念結果：

```text
name = pytorch
type = compute
gpu_required = true
gpu_name = ...
```

vLLM：

```text
name = vllm
type = llm-inference
gpu_required = true
endpoint = ...
```

Runtime Metadata 可以讓上層平台知道目前正在使用什麼 Backend。

---

# 23. vLLM Runtime Manager 驗證

執行：

```python
from runtime.manager import RuntimeManager

manager = RuntimeManager()

runtime = manager.get_runtime(
    "vllm",
    endpoint="http://10.148.0.10:30800"
)

print(type(runtime).__name__)
print(runtime.get_info())
```

結果：

```text
VLLMRuntime

{
    'name': 'vllm',
    'type': 'llm-inference',
    'gpu_required': True,
    'endpoint': 'http://10.148.0.10:30800'
}
```

代表：

```text
RuntimeManager
      ↓
"vllm"
      ↓
VLLMRuntime
```

正確建立。

---

# 24. vLLM initialize 驗證

執行：

```python
runtime.initialize()
```

結果：

```text
vLLM Runtime initialized successfully
```

代表：

```text
RuntimeManager
      ↓
VLLMRuntime
      ↓
/v1/models
      ↓
SG vLLM Server
```

連線成功。

---

# 25. Singapore Node IP 變更

Day3 Singapore GPU Node Internal IP：

```text
10.148.0.9
```

GPU Node 重建後改成：

```text
10.148.0.10
```

因此原本：

```text
http://10.148.0.9:30800
```

發生：

```text
TimeoutError
```

重新取得 Node：

```bash
kubectl \
  --context=gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  get nodes -o wide
```

取得：

```text
INTERNAL-IP
10.148.0.10
```

更新 Endpoint 後：

```text
http://10.148.0.10:30800
```

initialize 成功。

---

# 26. vLLM Inference 驗證

透過 RuntimeManager：

```python
runtime = manager.get_runtime(
    "vllm",
    endpoint="http://10.148.0.10:30800"
)
```

執行：

```python
result = runtime.run({
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "messages": [
        {
            "role": "user",
            "content": "Explain GPU inference in one short sentence."
        }
    ],
    "max_tokens": 64
})
```

實際回應：

```text
GPU inference is the use of graphics processing units (GPUs) to perform inference tasks on large-scale data sets or models, allowing for parallel computing and faster execution compared to traditional CPU-based approaches.
```

證明：

```text
RuntimeManager
      ↓
VLLMRuntime
      ↓
vLLM API
      ↓
Qwen
      ↓
NVIDIA L4
      ↓
Inference Result
```

完整成功。

---

# 27. PyTorch 與 vLLM 的關係

PyTorch 不只用於 Training。

PyTorch 可以：

```text
PyTorch
├── Training
└── Inference
```

vLLM 則專門處理：

```text
LLM Inference / Serving
```

因此平台目前：

```text
RuntimeManager
        │
        ├── PyTorchRuntime
        │     ↓
        │ Compute / Training / General Inference
        │
        └── VLLMRuntime
              ↓
          LLM Inference
```

兩者不是：

```text
vLLM 取代 PyTorch
```

而是不同 Runtime Backend。

---

# 28. train.py 的定位

目前：

```text
runtime/pytorch/train.py
```

仍然是 Day2 的：

```text
Training Workload
```

執行流程仍是：

```text
train.py
↓
PyTorch
↓
CUDA
↓
NVIDIA L4
```

Day4 沒有為了形式強制重構 `train.py`。

今天建立的是：

```text
Runtime Abstraction Layer
```

讓後面的 Benchmark Engine 可以透過 RuntimeManager 選擇適合的 Runtime。

---

# 29. Day4 File Structure

Day4 清理測試檔與 Python Cache 後：

```text
runtime/
├── base.py
├── manager.py
│
├── pytorch/
│   ├── __init__.py
│   ├── runtime.py
│   └── train.py
│
└── vllm/
    └── runtime.py
```

刪除：

```text
runtime/test_manager.py
```

以及：

```text
__pycache__/
```

避免留下臨時測試檔與 Cache。

---

# 30. Day4 Final Architecture

```text
                    AI Platform
                         │
                         ▼
                  Runtime Manager
                         │
                         ▼
                  Runtime Interface
                    /           \
                   /             \
                  ▼               ▼
          PyTorchRuntime      VLLMRuntime
                │                  │
                ▼                  ▼
             PyTorch           vLLM Server
                │                  │
                ▼                  ▼
              CUDA               Qwen
                 \                /
                  \              /
                   ▼            ▼
                    NVIDIA L4
```

---

# 31. Day4 完成成果

Week15 Day4 完成：

```text
Runtime Interface
+
Runtime Manager
+
PyTorch Runtime Adapter
+
vLLM Runtime Adapter
+
Lazy Import
+
Runtime Metadata
+
Runtime Switching
+
Real vLLM Inference Verification
```

平台從：

```text
程式直接綁死 Runtime
```

進化成：

```text
Platform
   ↓
Runtime Manager
   ↓
Selected Runtime
```

---

# 32. Runtime Extensibility

目前：

```text
RuntimeManager
├── PyTorchRuntime
└── VLLMRuntime
```

Runtime Abstraction 已經保留擴充能力。

後續 Performance Engineering 階段可以加入：

```text
ONNX Runtime
TensorRT
```

架構可以演進成：

```text
RuntimeManager
├── PyTorchRuntime
├── VLLMRuntime
├── ONNXRuntime
└── TensorRTRuntime
```

上層平台不需要因新增 Backend 而重新設計。

---

# 33. Day4 與後續 Week15 的關係

Day4：

```text
Runtime Abstraction
```

Day5：

```text
Benchmark Engine
```

利用不同 Runtime 執行：

```text
Training Benchmark
Inference Benchmark
```

Day6：

```text
Performance Analyzer
```

分析：

```text
GPU Bottleneck
CPU Bottleneck
Memory Bottleneck
DataLoader Bottleneck
```

Day7：

```text
AI Runtime Platform v1
```

完整整合：

```text
Runtime
↓
Training / Inference
↓
Benchmark
↓
Performance Analyzer
↓
Prometheus
↓
Grafana
```

---

# Interview Review

## Q1：為什麼需要 Runtime Abstraction？

如果上層平台直接依賴 PyTorch 或 vLLM，新增 Runtime 時就需要修改大量平台邏輯。

Runtime Abstraction 透過：

```text
Runtime Interface
+
Runtime Manager
+
Runtime Adapter
```

將上層平台與底層 Runtime 解耦。

因此新增 Runtime 時主要只需要：

```text
實作 Runtime Interface
↓
註冊到 RuntimeManager
```

上層邏輯可以保持不變。

---

## Q2：RuntimeManager 的作用是什麼？

RuntimeManager 負責根據 Runtime Name 選擇並建立對應 Backend。

例如：

```text
"pytorch"
↓
PyTorchRuntime
```

以及：

```text
"vllm"
↓
VLLMRuntime
```

因此上層只需要與 RuntimeManager 溝通，而不需要直接依賴各個 Runtime Implementation。

---

# Week15 Day4 Complete

```text
Runtime Interface
        ↓
Runtime Manager
        ↓
Runtime Switching
     /             \
PyTorchRuntime   VLLMRuntime
     │               │
 PyTorch            vLLM
     │               │
     └───────┬───────┘
             ▼
         NVIDIA L4
```

Day4 完成後，平台正式開始具備：

```text
Modular AI Runtime Architecture
```
