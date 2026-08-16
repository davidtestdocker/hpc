import time

from runtime.base import Runtime


class PyTorchRuntime(Runtime):
    def __init__(self):
        # Runtime dependencies are loaded only during initialization
        self.torch = None
        self.device = None
        self.gpu_name = None

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

    def run(self, request=None):
        # Ensure the runtime has been initialized
        if self.torch is None or self.device is None:
            raise RuntimeError("Runtime is not initialized")

        # Run a small GPU computation
        a = self.torch.randn((2048, 2048), device=self.device)
        b = self.torch.randn((2048, 2048), device=self.device)
        c = self.torch.matmul(a, b)

        # Wait until GPU computation is completed
        self.torch.cuda.synchronize()

        return {
            "status": "completed",
            "result_device": str(c.device),
        }

    def get_info(self):
        # Return runtime metadata without requiring initialization
        return {
            "name": "pytorch",
            "type": "compute",
            "gpu_required": True,
            "gpu_name": self.gpu_name,
        }


def main():
    runtime = PyTorchRuntime()

    runtime.initialize()
    result = runtime.run()

    print("PyTorch Runtime Ready")
    print(runtime.get_info())
    print(result)

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
