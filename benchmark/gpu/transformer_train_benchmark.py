"""Repeatable single-GPU synthetic Transformer language-model training baseline."""

import json
import math
import os
import statistics
import time

import torch


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile without an extra numerical dependency."""
    ordered = sorted(values)
    index = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return ordered[index]


class TinyLanguageModel(torch.nn.Module):
    """Small decoder-free Transformer used to exercise forward/backward GPU kernels."""

    def __init__(self, vocab_size: int, hidden_size: int, layers: int, heads: int):
        super().__init__()
        self.embedding = torch.nn.Embedding(vocab_size, hidden_size)
        encoder_layer = torch.nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=heads,
            dim_feedforward=hidden_size * 4,
            dropout=0.0,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = torch.nn.TransformerEncoder(encoder_layer, num_layers=layers)
        self.output = torch.nn.Linear(hidden_size, vocab_size, bias=False)

    def forward(self, token_ids):
        hidden = self.embedding(token_ids)
        return self.output(self.encoder(hidden))


def train_step(model, optimizer, inputs, targets, vocab_size):
    """Run one BF16 training step and return its scalar loss."""
    optimizer.zero_grad(set_to_none=True)
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        logits = model(inputs)
        loss = torch.nn.functional.cross_entropy(
            logits.reshape(-1, vocab_size),
            targets.reshape(-1),
        )
    loss.backward()
    optimizer.step()
    return float(loss.detach())


def main():
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16-capable GPU is required")

    # Environment variables make the workload tunable while defaults stay small for the L4 lab.
    batch_size = int(os.getenv("BATCH_SIZE", "8"))
    sequence_length = int(os.getenv("SEQUENCE_LENGTH", "256"))
    vocab_size = int(os.getenv("VOCAB_SIZE", "4096"))
    hidden_size = int(os.getenv("HIDDEN_SIZE", "512"))
    layers = int(os.getenv("LAYERS", "4"))
    heads = int(os.getenv("HEADS", "8"))
    warmup_steps = int(os.getenv("WARMUP_STEPS", "10"))
    measured_steps = int(os.getenv("MEASURED_STEPS", "20"))
    repetitions = int(os.getenv("REPETITIONS", "3"))

    torch.manual_seed(20260921)
    torch.cuda.manual_seed_all(20260921)
    device = torch.device("cuda:0")
    model = TinyLanguageModel(vocab_size, hidden_size, layers, heads).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    inputs = torch.randint(
        0, vocab_size, (batch_size, sequence_length), device=device,
    )
    targets = torch.randint(
        0, vocab_size, (batch_size, sequence_length), device=device,
    )

    for _ in range(warmup_steps):
        train_step(model, optimizer, inputs, targets, vocab_size)
    torch.cuda.synchronize()

    runs = []
    for repetition in range(1, repetitions + 1):
        torch.cuda.reset_peak_memory_stats()
        latencies_ms = []
        losses = []
        for _ in range(measured_steps):
            torch.cuda.synchronize()
            started = time.perf_counter()
            losses.append(train_step(model, optimizer, inputs, targets, vocab_size))
            torch.cuda.synchronize()
            latencies_ms.append((time.perf_counter() - started) * 1000)

        duration_seconds = sum(latencies_ms) / 1000
        samples = batch_size * measured_steps
        tokens = samples * sequence_length
        runs.append({
            "repetition": repetition,
            "mean_step_ms": statistics.fmean(latencies_ms),
            "median_step_ms": statistics.median(latencies_ms),
            "p95_step_ms": percentile(latencies_ms, 0.95),
            "samples_per_second": samples / duration_seconds,
            "tokens_per_second": tokens / duration_seconds,
            "final_loss": losses[-1],
            "peak_memory_mib": torch.cuda.max_memory_allocated() / 1024 / 1024,
        })

    result = {
        "workload": "synthetic-transformer-language-model-training",
        "scope": "single-GPU BF16 kernel baseline; not pretrained LLM quality or multi-GPU scaling",
        "gpu": torch.cuda.get_device_name(device),
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "seed": 20260921,
        "config": {
            "batch_size": batch_size,
            "sequence_length": sequence_length,
            "vocab_size": vocab_size,
            "hidden_size": hidden_size,
            "layers": layers,
            "heads": heads,
            "warmup_steps": warmup_steps,
            "measured_steps": measured_steps,
            "repetitions": repetitions,
            "precision": "bfloat16-autocast",
        },
        "runs": runs,
        "aggregate": {
            "mean_step_ms": statistics.fmean(run["mean_step_ms"] for run in runs),
            "mean_tokens_per_second": statistics.fmean(
                run["tokens_per_second"] for run in runs
            ),
            "tokens_per_second_cv_percent": (
                statistics.stdev(run["tokens_per_second"] for run in runs)
                / statistics.fmean(run["tokens_per_second"] for run in runs)
                * 100
            ),
        },
    }
    print("RESULT_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
