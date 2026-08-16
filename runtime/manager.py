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
