"""驗證分析口徑：CUDA kernel 不與 CPU wrapper 重複加總，缺資料或 hash 不符即失敗。

這些是離線分析測試；真實 CUDA capture 與模型因果性檢查在 GPU 實驗中驗證。
"""
import json

import pytest

from analysis.causal_lm_report import summarize_runs, summarize_trace, verify_bundle


def test_trace_counts_cuda_kernels_once_not_cpu_wrappers():
    result = summarize_trace({'traceEvents': [
        {'cat': 'cpu_op', 'ph': 'X', 'name': 'matmul', 'dur': 100},
        {'cat': 'kernel', 'ph': 'X', 'name': 'gemm', 'dur': 20},
        {'cat': 'kernel', 'ph': 'X', 'name': 'gemm', 'dur': 30},
        {'cat': 'kernel', 'ph': 'X', 'name': 'activation', 'dur': 50},
    ]})
    assert result['summed_kernel_duration_us'] == 100
    assert result['kernel_events'] == 3
    assert result['top_kernels'][0]['share_of_summed_kernel_time_percent'] == 50


def test_missing_cuda_events_fail_instead_of_claiming_gpu_profile():
    with pytest.raises(ValueError, match='no CUDA'):
        summarize_trace({'traceEvents': []})


def test_insufficient_repeats_fail_instead_of_reporting_stable_comparison():
    with pytest.raises(ValueError, match='three runs'):
        summarize_runs([])


def test_modified_raw_evidence_is_rejected(tmp_path):
    (tmp_path / 'result.json').write_text('{}')
    (tmp_path / 'evidence.json').write_text(json.dumps({'sha256': {'result.json': 'incorrect'}}))
    with pytest.raises(ValueError, match='checksum mismatch'):
        verify_bundle(tmp_path)
