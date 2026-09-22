"""離線分析：核對原始證據 hash，再分別彙整未開 profiler 的量測與 CUDA traces。

效能數字來自 runs；kernel 分布來自 traces，兩者不混成同一個計時結果。
報告解讀見 docs/performance/causal-lm-l4-20260922.md。
"""
import argparse
import gzip
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


def verify_bundle(directory):
    """比對 evidence.json 登錄的 SHA-256，拒絕分析已被改動的原始結果。"""
    evidence = json.loads((directory / 'evidence.json').read_text())
    for name, expected in evidence['sha256'].items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Artifact checksum mismatch: {name}')


def summarize_runs(runs):
    """各 batch 至少三次；保留均值、範圍與 CV，計算 8→16 的相對變化。"""
    groups = {}
    for batch in (8, 16):
        selected = [r for r in runs if r['batch_size'] == batch]
        if len(selected) < 3:
            raise ValueError('At least three runs per batch required')
        throughput = [r['tokens_per_second'] for r in selected]
        if not all(math.isfinite(x) and x > 0 for x in throughput):
            raise ValueError('Throughput must be finite and positive')
        # CV = 樣本標準差／均值，表示重複測量波動；不是信賴區間。
        # peak memory 取三次中的最大值；throughput 與 mean step 則各自取平均。
        groups[str(batch)] = {
            'repetitions': len(selected),
            'mean_tokens_per_second': statistics.fmean(throughput),
            'min_tokens_per_second': min(throughput), 'max_tokens_per_second': max(throughput),
            'throughput_cv_percent': statistics.stdev(throughput) / statistics.fmean(throughput) * 100,
            'mean_step_ms': statistics.fmean(r['mean_step_ms'] for r in selected),
            'max_peak_allocated_mib': max(r['peak_allocated_mib'] for r in selected),
            'initial_loss': [r['initial_loss'] for r in selected],
            'final_loss': [r['final_loss'] for r in selected],
        }
    # throughput 上升可代表收益，但 latency／memory 上升則是同時付出的代價。
    change = {metric: (groups['16'][metric] / groups['8'][metric] - 1) * 100
              for metric in ('mean_tokens_per_second', 'mean_step_ms', 'max_peak_allocated_mib')}
    return {'batches': groups, 'batch8_to_16_change_percent': change}


def summarize_trace(trace):
    """只計 CUDA kernel 的完整 duration 事件，排除 CPU wrapper 的重複歸因。"""
    # Chrome trace 的 ph=X 代表含持續時間的完整事件；dur 單位為微秒。
    kernels = [e for e in trace.get('traceEvents', [])
               if e.get('cat') == 'kernel' and e.get('ph') == 'X' and e.get('dur', 0) > 0]
    if not kernels:
        raise ValueError('Trace has no CUDA kernel duration events')
    totals = defaultdict(float)
    counts = defaultdict(int)
    for event in kernels:
        totals[event['name']] += event['dur']
        counts[event['name']] += 1
    total = sum(totals.values())
    # 這是依名稱選出的 kernel 群組，不是完整且互斥的硬體瓶頸分類。
    # duration 相加不是 wall time，也不能直接當 GPU 使用率。
    families = {
        'multi_tensor_named_kernels': sum(v for k, v in totals.items() if 'multi_tensor' in k),
        'gemm_named_kernels': sum(v for k, v in totals.items() if 'gemm' in k.lower()),
    }
    return {'kernel_events': len(kernels), 'summed_kernel_duration_us': total,
            'selected_name_families_us': families,
            'note': 'Sum of kernel durations, not wall time or GPU utilization; profiler overhead applies',
            'top_kernels': [{'name': k, 'count': counts[k], 'duration_us': v,
                             'share_of_summed_kernel_time_percent': v / total * 100}
                            for k, v in sorted(totals.items(), key=lambda x: x[1], reverse=True)[:12]]}


def main():
    """讀取一個已完成的 artifact 目錄，產出可重算的 summary.json。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    verify_bundle(args.directory)
    result = json.loads((args.directory / 'result.json').read_text())
    summary = summarize_runs(result['runs'])
    summary['profiles'] = {}
    for batch in (8, 16):
        with gzip.open(args.directory / f'batch{batch}.trace.json.gz', 'rt') as f:
            summary['profiles'][str(batch)] = summarize_trace(json.load(f))
    (args.directory / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
