"""Small byte-token causal LM: controlled batch comparison and separate CUDA traces."""
import gzip
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch.profiler import ProfilerActivity, profile, record_function

SEED = 20260922
SEQ = 256
HIDDEN = 512
LAYERS = 4


class CausalLM(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.tokens = torch.nn.Embedding(256, HIDDEN)
        self.positions = torch.nn.Embedding(SEQ, HIDDEN)
        layer = torch.nn.TransformerEncoderLayer(
            HIDDEN, 8, HIDDEN * 4, dropout=0.0, activation='gelu',
            batch_first=True, norm_first=True,
        )
        self.blocks = torch.nn.TransformerEncoder(layer, LAYERS, enable_nested_tensor=False)
        self.norm = torch.nn.LayerNorm(HIDDEN)
        self.head = torch.nn.Linear(HIDDEN, 256, bias=False)
        self.register_buffer('mask', torch.triu(torch.ones(SEQ, SEQ, dtype=torch.bool), 1))

    def forward(self, tokens):
        length = tokens.shape[1]
        x = self.tokens(tokens) + self.positions(torch.arange(length, device=tokens.device))
        x = self.blocks(x, mask=self.mask[:length, :length], is_causal=True)
        return self.head(self.norm(x))


def step(model, optimizer, batches, number):
    x, y = batches[number % len(batches)]
    with record_function('train.zero_grad'):
        optimizer.zero_grad(set_to_none=True)
    with record_function('train.forward_loss'), torch.autocast('cuda', dtype=torch.bfloat16):
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(logits.reshape(-1, 256), y.reshape(-1))
    with record_function('train.backward'):
        loss.backward()
    with record_function('train.optimizer'):
        optimizer.step()
    return loss.detach()


def prepare(corpus, batch):
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    model = CausalLM().cuda().train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    # Same ordered examples for both settings; batch 16 groups twice as many examples.
    generator = torch.Generator().manual_seed(SEED + 1)
    starts = torch.randint(len(corpus) - SEQ, (128,), generator=generator)
    windows = torch.stack([corpus[s:s + SEQ + 1] for s in starts]).cuda()
    batches = [(windows[i:i + batch, :-1], windows[i:i + batch, 1:])
               for i in range(0, len(windows), batch)]
    return model, optimizer, batches


def telemetry(stop, rows):
    while not stop.is_set():
        try:
            sample = subprocess.check_output([
                'nvidia-smi', '--query-gpu=timestamp,uuid,utilization.gpu,memory.used,power.draw,temperature.gpu',
                '--format=csv,noheader,nounits',
            ], text=True, timeout=5).strip()
            rows.append({'unix_time': time.time(), 'sample': sample})
        except (OSError, subprocess.SubprocessError) as exc:
            rows.append({'error': str(exc)})
        stop.wait(1)


def main():
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError('BF16 CUDA device required')
    output = Path(os.getenv('OUTPUT_DIR', '/results'))
    output.mkdir(parents=True, exist_ok=True)
    source = Path(os.getenv('CORPUS_PATH', '/benchmark/corpus.txt')).read_bytes()
    if len(source) <= SEQ:
        raise ValueError('Corpus too short')
    corpus = torch.tensor(list(source), dtype=torch.long)
    torch.set_num_threads(2)
    warmup, measured = 20, 40
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'single-L4 small causal LM training on local UTF-8 bytes; not pretrained LLM quality',
        'config': {'seed': SEED, 'sequence_length': SEQ, 'hidden': HIDDEN, 'layers': LAYERS,
                   'heads': 8, 'vocab': 256, 'precision': 'BF16 autocast', 'optimizer': 'AdamW',
                   'learning_rate': 3e-4, 'dropout': 0.0, 'warmup': warmup, 'measured_steps': measured,
                   'order': [8, 16, 16, 8, 8, 16], 'token_unit': 'UTF-8 byte',
                   'data_residency': 'preloaded GPU; excludes tokenizer/storage/data-loader'},
        'environment': {'torch': torch.__version__, 'cuda': torch.version.cuda,
                        'gpu': torch.cuda.get_device_name(0), 'python': platform.python_version(),
                        'hostname': platform.node(), 'cpu_threads': torch.get_num_threads(),
                        'nvidia_smi': subprocess.check_output(['nvidia-smi'], text=True)},
        'corpus': {'bytes': len(source), 'sha256': hashlib.sha256(source).hexdigest(),
                   'source': 'repository README.md snapshot, UTF-8 bytes; 128 fixed windows'},
        'runs': [], 'profiles': {},
    }
    rows, stop = [], threading.Event()
    thread = threading.Thread(target=telemetry, args=(stop, rows), daemon=True)
    thread.start()
    try:
        for index, batch in enumerate(result['config']['order']):
            model, optimizer, batches = prepare(corpus, batch)
            result['parameter_count'] = sum(p.numel() for p in model.parameters())
            if index == 0:
                # Changing future tokens must not change prefix logits.
                with torch.no_grad():
                    x = batches[0][0][:1].clone()
                    before = model(x)[:, :32]
                    x[:, 32:] = (x[:, 32:] + 1) % 256
                    difference = (before - model(x)[:, :32]).abs().max().item()
                    assert difference < 1e-5, difference
                    result['causality_check_max_prefix_difference'] = difference
                    del before, x
            initial_loss = float(step(model, optimizer, batches, 0))
            for n in range(warmup):
                step(model, optimizer, batches, n)
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
            latencies = []
            started_at = time.time()
            for n in range(measured):
                start = time.perf_counter()
                loss = step(model, optimizer, batches, n)
                torch.cuda.synchronize()
                latencies.append((time.perf_counter() - start) * 1000)
            final_loss = float(loss)
            assert math.isfinite(final_loss)
            result['runs'].append({
                'order_index': index, 'batch_size': batch, 'started_at_unix': started_at,
                'finished_at_unix': time.time(), 'step_ms': latencies,
                'mean_step_ms': statistics.fmean(latencies),
                'p95_step_ms': sorted(latencies)[math.ceil(.95 * len(latencies)) - 1],
                'tokens_per_second': batch * SEQ * measured / (sum(latencies) / 1000),
                'peak_allocated_mib': torch.cuda.max_memory_allocated() / 2**20,
                'peak_reserved_mib': torch.cuda.max_memory_reserved() / 2**20,
                'initial_loss': initial_loss, 'final_loss': final_loss,
            })
            del model, optimizer, batches, loss
            torch.cuda.empty_cache()
            print(f'Measured case {index + 1}/6, batch={batch}', flush=True)

        # Profiler overhead is excluded from all throughput numbers above.
        for batch in (8, 16):
            model, optimizer, batches = prepare(corpus, batch)
            for n in range(warmup):
                step(model, optimizer, batches, n)
            torch.cuda.synchronize()
            with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
                         record_shapes=True, profile_memory=True) as prof:
                for n in range(5):
                    step(model, optimizer, batches, n)
                    prof.step()
                torch.cuda.synchronize()
            events = prof.key_averages()
            operators = [{'name': e.key, 'calls': e.count,
                          'self_cpu_us': e.self_cpu_time_total,
                          'self_device_us': e.self_device_time_total,
                          'device_total_us': e.device_time_total}
                         for e in events]
            operators.sort(key=lambda e: e['self_device_us'], reverse=True)
            assert sum(e['self_device_us'] for e in operators) > 0, 'CUDA profiler events absent'
            result['profiles'][str(batch)] = {'steps': 5, 'operators': operators}
            prof.export_chrome_trace(str(output / f'batch{batch}.trace.json'))
            with gzip.open(output / f'batch{batch}.trace.json.gz', 'wb') as f:
                f.write((output / f'batch{batch}.trace.json').read_bytes())
            del model, optimizer, batches, prof, events
            torch.cuda.empty_cache()
    finally:
        stop.set()
        thread.join(timeout=6)
        result['telemetry'] = rows
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print('BENCHMARK_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
