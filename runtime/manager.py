# 依名稱選擇 runtime，延後 import 可避免啟動時就載入所有 GPU 套件。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
# class 定義 RuntimeManager 類別，封裝相關資料與方法。
class RuntimeManager:
    # 根據名稱建立對應 runtime；**kwargs 接收額外的具名參數。
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
