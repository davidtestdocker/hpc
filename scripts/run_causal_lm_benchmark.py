"""單 GPU 實驗入口：保存快照 → 建立 Pod → 等待量測 → 取回證據 → 清理。

本機只需 kubectl／PyYAML，PyTorch 在 GPU 容器內執行。
重跑步驟與限制見 docs/runbooks/causal-lm-benchmark.md。
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(context, name, output):
    """用明確 context 和唯一名稱執行一次實驗；失敗時保留現場供排查。"""
    # exist_ok=False 防止重跑覆寫舊證據；目錄建立後即保存本次輸入。
    output.mkdir(parents=True, exist_ok=False)
    base = ['kubectl', '--context', context, '--request-timeout=30s', '-n', 'hpc-platform-dev']

    def kubectl(args, data=None):
        """以參數陣列呼叫 kubectl；可用 stdin 傳 manifest，失敗立即拋出例外。"""
        return subprocess.check_output(base + args, input=data, timeout=90)

    # corpus 和程式可能日後改動，因此本次快照與現行原始碼分開保存。
    source = (ROOT / 'benchmark/gpu/causal_lm_benchmark.py').read_text()
    corpus = (ROOT / 'README.md').read_text()
    (output / 'corpus.txt').write_text(corpus)
    (output / 'benchmark-source.py').write_text(source)
    cm = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': name},
          'data': {'causal_lm_benchmark.py': source, 'corpus.txt': corpus}}
    # nodeSelector 決定 GPU pool；toleration 允許接受 GPU taint。
    # nvidia.com/gpu=1 在此叢集是一個 time-sharing share，不是額外建立一張 GPU。
    # 成功後 sleep 保留容器供 exec 取檔；emptyDir 隨 Pod 刪除，必須先收回結果。
    pod = {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': name,
           'labels': {'app': 'causal-lm-benchmark'}}, 'spec': {
        'restartPolicy': 'Never', 'activeDeadlineSeconds': 1200,
        'nodeSelector': {'cloud.google.com/gke-nodepool': 'gpu-pool'},
        'tolerations': [{'key': 'nvidia.com/gpu', 'operator': 'Equal',
                         'value': 'present', 'effect': 'NoSchedule'}],
        'containers': [{'name': 'benchmark',
            'image': 'pytorch/pytorch:2.12.0-cuda12.6-cudnn9-runtime',
            'command': ['sh', '-c', 'python /benchmark/causal_lm_benchmark.py && sleep 900'],
            'resources': {'requests': {'cpu': '2', 'memory': '6Gi', 'nvidia.com/gpu': '1'},
                          'limits': {'cpu': '4', 'memory': '10Gi', 'nvidia.com/gpu': '1'}},
            'volumeMounts': [{'name': 'script', 'mountPath': '/benchmark', 'readOnly': True},
                             {'name': 'results', 'mountPath': '/results'}]}],
        'volumes': [{'name': 'script', 'configMap': {'name': name}},
                    {'name': 'results', 'emptyDir': {}}],
    }}
    manifests = yaml.safe_dump_all([cm, pod])
    (output / 'manifest.yaml').write_text(manifests)
    # create 遇到同名資源會失敗，避免覆寫其他實驗；這一步可能留下部分已建立資源。
    print(kubectl(['create', '-f', '-'], manifests.encode()).decode(), flush=True)
    # monotonic 不受系統校時影響；Running 只代表容器存活，還要看到完成標記。
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        status = json.loads(kubectl(['get', 'pod', name, '-o', 'json']))
        (output / 'pod.json').write_text(json.dumps(status, indent=2) + '\n')
        phase = status['status']['phase']
        if phase == 'Running':
            log = kubectl(['logs', name]).decode()
            (output / 'run.log').write_text(log)
            if 'BENCHMARK_COMPLETE' in log:
                break
        if phase in {'Failed', 'Succeeded'}:
            (output / 'run.log').write_bytes(kubectl(['logs', name]))
            raise RuntimeError(f'Benchmark ended unexpectedly: {phase}; keep Pod for diagnosis')
        time.sleep(5)
    else:
        raise TimeoutError('Benchmark deadline; Pod retained for diagnosis')

    # 用 bytes 取回壓縮 trace，避免文字解碼破壞檔案；再確認兩組結果皆存在。
    artifacts = ['result.json', 'batch8.trace.json.gz', 'batch16.trace.json.gz']
    for artifact in artifacts:
        (output / artifact).write_bytes(kubectl(['exec', name, '--', 'cat', '/results/' + artifact]))
    results = json.loads((output / 'result.json').read_text())
    assert len(results['runs']) == 6 and len(results['profiles']) == 2
    # imageID 保存實際 digest；hashes 用來偵測原始證據之後是否被更動。
    evidence = {'context': context, 'pod': name, 'node': status['spec']['nodeName'],
                'image_id': status['status']['containerStatuses'][0]['imageID'],
                'sha256': {f: hashlib.sha256((output / f).read_bytes()).hexdigest()
                           for f in artifacts + ['corpus.txt', 'benchmark-source.py']},
                'passed': True}
    # 成功收回證據才清理本次具名 Pod／ConfigMap；不刪節點、PVC 或其他工作。
    print(kubectl(['delete', 'pod', name, '--wait=false']).decode(), flush=True)
    print(kubectl(['delete', 'configmap', name]).decode(), flush=True)
    evidence['cleanup'] = 'temporary Pod deletion requested; ConfigMap deleted; artifacts retained'
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2), flush=True)


if __name__ == '__main__':
    # --execute 是明確的操作開關，因為此程式會建立、執行並清理叢集資源。
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not args.execute:
        parser.error('--execute is required to create and run the temporary GPU Pod')
    run(args.context, args.name, args.output)
