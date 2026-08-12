import time
import torch


def validate_runtime():
    # Verify that PyTorch can access CUDA
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    # Get the GPU assigned to this runtime
    device = torch.device("cuda:0")
    gpu_name = torch.cuda.get_device_name(device)

    # Run a small GPU computation to verify CUDA execution
    a = torch.randn((2048, 2048), device=device)
    b = torch.randn((2048, 2048), device=device)
    c = torch.matmul(a, b)

    # Wait until the GPU computation is completed
    torch.cuda.synchronize()

    print("PyTorch Runtime Ready")
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"GPU Device: {gpu_name}")
    print(f"Result Device: {c.device}")


def main():
    # Validate the runtime when the container starts
    validate_runtime()

    # Keep the runtime process alive
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
