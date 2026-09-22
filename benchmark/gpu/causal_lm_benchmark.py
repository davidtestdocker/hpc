"""小型 byte-token causal LM：固定文字資料、交錯 batch 比較與獨立 CUDA profiling。

流程：讀 corpus → 固定 seed 建模 → 因果性檢查 → 暖機與計時 → 另跑 profiler。
本程式在 GPU Pod 內執行；本機入口是 scripts/run_causal_lm_benchmark.py。
結果目錄的 benchmark-source.py 是當時實測快照，現行註解更新不回寫該快照。
"""
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
    """以因果遮罩限制 attention 的小型 Transformer，輸出每個位置的下一 byte logits。"""
    def __init__(self):
        """建立 token／位置 embedding、四層 Transformer、正規化與輸出投影。"""
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
        # 上三角 True 遮住未來位置；buffer 隨 model 移到 GPU，但不參與梯度更新。
        self.register_buffer('mask', torch.triu(torch.ones(SEQ, SEQ, dtype=torch.bool), 1))

    def forward(self, tokens):
        """輸入 [batch, sequence]，回傳 [batch, sequence, 256] 的詞彙 logits。"""
        length = tokens.shape[1]
        x = self.tokens(tokens) + self.positions(torch.arange(length, device=tokens.device))
        x = self.blocks(x, mask=self.mask[:length, :length], is_causal=True)
        return self.head(self.norm(x))


def step(model, optimizer, batches, number):
    """一次訓練更新：清梯度 → BF16 forward／loss → backward → AdamW。

    record_function 為 profiler 標記階段；回傳仍在 GPU 的 detached loss，
    避免每步讀 scalar 引入額外同步。計時迴圈會明確 synchronize。
    """
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
    """每次測量重建相同初始權重和固定語料窗口，只改 batch 的分組大小。"""
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    model = CausalLM().cuda().train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    # 兩組共享相同、有順序的 128 個窗口；batch 16 每步處理兩倍的例子。
    generator = torch.Generator().manual_seed(SEED + 1)
    starts = torch.randint(len(corpus) - SEQ, (128,), generator=generator)
    windows = torch.stack([corpus[s:s + SEQ + 1] for s in starts]).cuda()
    # 每個窗口長 SEQ+1；輸入去掉最後一 byte、target 去掉第一 byte，形成 next-byte 任務。
    batches = [(windows[i:i + batch, :-1], windows[i:i + batch, 1:])
               for i in range(0, len(windows), batch)]
    return model, optimizer, batches


def telemetry(stop, rows):
    """背景約每秒收集一次 nvidia-smi；記錄時間以區分暖機、計時與 profiler 階段。"""
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
    """完成六次非 profiler 量測、兩組 CUDA trace，最後保存 JSON 與遙測。"""
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError('BF16 CUDA device required')
    output = Path(os.getenv('OUTPUT_DIR', '/results'))
    output.mkdir(parents=True, exist_ok=True)
    source = Path(os.getenv('CORPUS_PATH', '/benchmark/corpus.txt')).read_bytes()
    if len(source) <= SEQ:
        raise ValueError('Corpus too short')
    # 每個 UTF-8 byte 是一個 token；此處 tokens/s 不能與 BPE tokenizer 的數字直接比較。
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
        # 交錯 8、16、16、8、8、16，降低先後順序的影響；所有測次都保存，不挑最佳值。
        for index, batch in enumerate(result['config']['order']):
            model, optimizer, batches = prepare(corpus, batch)
            result['parameter_count'] = sum(p.numel() for p in model.parameters())
            if index == 0:
                # 因果性檢查：修改未來 tokens，前綴 logits 應不變，確認遮罩真的生效。
                with torch.no_grad():
                    x = batches[0][0][:1].clone()
                    before = model(x)[:, :32]
                    x[:, 32:] = (x[:, 32:] + 1) % 256
                    difference = (before - model(x)[:, :32]).abs().max().item()
                    assert difference < 1e-5, difference
                    result['causality_check_max_prefix_difference'] = difference
                    del before, x
            # 初始 loss 會做一次更新，之後另外暖機 20 步；這些時間不納入正式測量。
            initial_loss = float(step(model, optimizer, batches, 0))
            for n in range(warmup):
                step(model, optimizer, batches, n)
            torch.cuda.synchronize()
            # 只重設峰值計數，不清空模型／optimizer；allocated 與 reserved 會分開保存。
            torch.cuda.reset_peak_memory_stats()
            latencies = []
            started_at = time.time()
            for n in range(measured):
                start = time.perf_counter()
                loss = step(model, optimizer, batches, n)
                # CUDA 非同步執行；等 GPU 完成再停表，避免只量到 CPU launch 時間。
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

        # profiling 另建模型、另暖機；record_shapes／profile_memory 的開銷不混進 throughput。
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
            # 保存 operator 統計供查閱；它可能有包含／重複歸因，不能把每列直接相加。
            # analysis/causal_lm_report.py 另從 raw trace 的 kernel events 計算分布。
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
        # 即使途中失敗也保存已完成的 runs 與 telemetry；檔案存在不等於實驗全部成功。
        stop.set()
        thread.join(timeout=6)
        result['telemetry'] = rows
        (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print('BENCHMARK_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
