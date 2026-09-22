<!-- current-curriculum: 2026-09-22 -->
# Week15 Day1 — PyTorch GPU runtime

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-PyTorch-Training-Runtime.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「PyTorch GPU runtime」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

torch.cuda.is_available 只驗證 runtime 可見性，還要實際建立 tensor 並執行 CUDA 工作。nvidia-smi 顯示的 CUDA 相容版本不一定是 PyTorch 內建 runtime 版本。

## 在現在的專案中

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從 runner 的 image 與 result 環境欄位追到 torch 版本，說明本機不裝 PyTorch也能離線讀報告，真正訓練發生在 GPU Pod。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '45,68p' 'scripts/run_causal_lm_benchmark.py'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/results/causal-lm-20260922/evidence.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week15/Day1—PyTorch-GPU-Runtime.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
