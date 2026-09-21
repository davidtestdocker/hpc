# PyTorch GPU runtime：初始化 CUDA，執行矩陣乘法並回傳裝置資訊。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import time

from runtime.base import Runtime


# class 定義 PyTorchRuntime 類別；括號內是繼承的父類別。
class PyTorchRuntime(Runtime):
    # 建構子：建立實例時初始化狀態；self 代表此物件本身。
    def __init__(self):
        # Runtime dependencies are loaded only during initialization
        self.torch = None
        self.device = None
        self.gpu_name = None

    # 準備 runtime 所需的模型或運算裝置。
    def initialize(self):
        # Load PyTorch only when this runtime is actually initialized
        import torch

        self.torch = torch

        # Verify that PyTorch can access CUDA
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available")

        # Get the GPU assigned to this runtime
        self.device = torch.device("cuda:0")
        self.gpu_name = torch.cuda.get_device_name(self.device)

    # 定義 run 函式；參數由呼叫端傳入，return 將結果交還呼叫端。
    def run(self, request=None):
        # Ensure the runtime has been initialized
        if self.torch is None or self.device is None:
            raise RuntimeError("Runtime is not initialized")

        # Run a small GPU computation
        # 建立兩個 2048×2048 的 GPU 隨機矩陣；matmul 計算矩陣乘法。
        a = self.torch.randn((2048, 2048), device=self.device)
        b = self.torch.randn((2048, 2048), device=self.device)
        c = self.torch.matmul(a, b)

        # Wait until GPU computation is completed
        # 等待非同步 CUDA 工作完成，確保後續計時包含 GPU 實際耗時。
        self.torch.cuda.synchronize()

        return {
            "status": "completed",
            "result_device": str(c.device),
        }

    # 回傳 runtime 的名稱、類型或裝置資訊。
    def get_info(self):
        # Return runtime metadata without requiring initialization
        return {
            "name": "pytorch",
            "type": "compute",
            "gpu_required": True,
            "gpu_name": self.gpu_name,
        }


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    runtime = PyTorchRuntime()

    runtime.initialize()
    result = runtime.run()

    print("PyTorch Runtime Ready")
    print(runtime.get_info())
    print(result)

    # 保持容器程序存活；sleep(60) 每次等待 60 秒，這裡不是持續執行 benchmark。
    while True:
        time.sleep(60)


# __name__ 在直接執行此檔時為 __main__；被 import 時不會執行這個入口。
if __name__ == "__main__":
    main()
