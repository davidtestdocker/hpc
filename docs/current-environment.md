# 現行教材的環境、練習與操作分級

版本：2026-09-22。先完成對應 Week 基礎，再選下面練習；不要求閱讀時同步部署雲端。所有命令以 repo 根目錄為起點；未安装工具時先跳過操作，不要直接在 GKE node 安裝或修改套件。

## 1. 四種不同的「有做」

| 類型 | 能證明什麼 | 不能證明什麼 |
|---|---|---|
| 閱讀 source／manifest | 儲存庫目前宣告或實作的行為 | 雲端已套用、工作成功 |
| 本機測試／離線渲染 | 特定程式契約與配置輸出 | 所有外部依賴可用 |
| 已保存實測結果 | 記錄日期／環境下的觀察 | 今天服務仍可用 |
| 本次重新實測 | 新記錄之環境與步驟下的結果 | 未涵蓋的 workload／故障模式 |

教材現行化屬文件工作，沒有為了更新文字而重跑雲端、故障注入或壓測。各次實測仍看 [Evidence Index](evidence/README.md)。不要把本機測試成功填成新雲端驗收。

## 2. 平台與獨立實驗的範圍

| 路徑 | 現行解讀 |
|---|---|
| GKE 主平台 | hpc-gpu-sg、hpc-platform-dev；API → 獨立 worker → CPU MPI JobSet → 自動回收 |
| 建置 | terraform/environments/gpu-sg → bootstrap_cluster → 主 overlay／deploy_platform |
| 訓練 | 單 L4、13M causal LM 的獨立 runner，未接 MPI API |
| Argo CD／CI | 既有 dev 路徑，不代表主 overlay 已 GitOps 對齊 |
| Slurm／Ray／vLLM／CPU DDP | 各自的獨立教材與歷史案例，不預設現有服務仍可連 |
| NetworkPolicy | 隔離 Calico 已驗收；主環境 enforcement 仍關閉 |
| Compose | 本機開發範例；不能直接當成現行完整平台的一鍵部署 |

同一張 L4 的 shares 不代表多卡。三個 MPI worker Pods 不代表三台 node。不同環境的性能數據不可合併算提升率。

## 3. Week1～2：先做不依賴叢集的小練習

Linux 自己的機器或開發容器可做下列唯讀觀察。輸出代表這台機器，不是 GKE 的數據：

```bash
ps -eo pid,ppid,stat,comm
nproc
free -h
df -h
```

判讀：PID 是程序身分；nproc 是可用處理單位數，不是 GPU 數；free 的 available 不等於 free；df 是容量，不是 I/O 延遲。現有 `monitoring/process_monitor.py` 只列 PID／名稱，沒有 CPU／RAM 採樣器。

以下 Python 小例子只在記憶體中操作，不連 Redis／DB：

```bash
python3 - <<'PY'
import json

def next_attempt(job):
    # 回傳新 dict，不直接改呼叫者的原資料。
    return {**job, "retry_count": job["retry_count"] + 1}

original = {"status": "accepted", "retry_count": 0}
updated = next_attempt(original)
encoded = json.dumps(updated)
decoded = json.loads(encoded)
assert original["retry_count"] == 0
assert decoded["retry_count"] == 1
print(type(encoded).__name__, type(decoded).__name__)
samples = [100, 110, 90]
print(sum(samples) / len(samples))
PY
```

應得到 `str dict` 和 `100.0`。這個例子教函式、return、list／dict／JSON，不代表實際 worker 就是這麼簡單；下一步再追真實程式的外部副作用。

## 4. Week4～10：在本機測契約，不啟動主叢集

需要 repo 的 `.venv` 與測試依賴。測試使用替身；不要因名稱有 worker 就認為會派發 MPI：

```bash
PYTHONPATH=. .venv/bin/pytest -q tests/test_api.py tests/test_worker.py
PYTHONPATH=. .venv/bin/pytest -q tests
```

本次改寫前的基準是 53 項 tests/ 通過，日後新增測試會改變數量。通過只支持斷言覆蓋範圍。既有 CI 執行 `python -m pytest`／`ruff check .`，不能把以上 scoped 測試通過說成整條遠端 CI 通過。

需要 Helm；以下只渲染到 stdout，不連叢集，也不安裝資源：

```bash
helm template api helm/api --namespace hpc-platform-dev -f kustomize/overlays/gpu-sg-platform/api-values.yaml
helm template redis helm/redis --namespace hpc-platform-dev -f kustomize/overlays/gpu-sg-platform/redis-values.yaml
```

判讀：第一份應能找到 api-worker 的 command 和資源設定，第二份能找到 PVC 與 /data 掛載。單 chart 渲染不包含所有 Kustomize patches；完整主 overlay 另看 `scripts/platform.py render`，可能需要 kubectl／Helm 以及本機可用 chart，離線渲染仍不等於 server dry-run。

Terraform 本機格式檢查不需要雲端認證，不修改檔案：

```bash
terraform fmt -check terraform/environments/gpu-sg
```

`fmt -check` 只檢查格式，不是 plan／validate／健康檢查。不需要為本課執行 init、apply、destroy 或匯出 state；state 可能含敏感內容。

## 5. Week11～16：離線重算，不改原始證據

先讀[量測方法](performance/causal-lm-l4-20260922.md)，再用現有純 Python 分析函式。這段只讀 bundle 並將摘要印出，不呼叫會重寫 summary.json 的 CLI：

```bash
PYTHONPATH=. .venv/bin/python - <<'PY'
from pathlib import Path
import json
from analysis.causal_lm_report import verify_bundle, summarize_runs

directory = Path("benchmark/results/causal-lm-20260922")
verify_bundle(directory)
raw = json.loads((directory / "result.json").read_text())
summary = summarize_runs(raw["runs"])
print(json.dumps(summary, indent=2))
PY
```

應讀到 batch 8／16 各三次，mean byte tokens/s 約 110,785／200,841；提升約 81.29%，step time 和 peak allocated 也增加。若 hashes 不符就先停下核對，不直接修改 hash 讓檢查通過。

接著讀 summarize_trace：只取 kernel／完整 duration 事件，避免加總 CPU wrapper 後重複計算。duration sum 不是 wall time；nvidia-smi 全程平均也不是每組 batch 使用率。

## 6. Week17～20：先用證據推演故障

先選一個案例，依序記錄「症狀 → 最後成功階段 → 下一個查詢對象 → 假說 → 如何驗證」：

- submitted 沒結果：先區分 worker 停止、JobSet 未完成、collector 讀取／回寫失敗。
- Pod Pending：先分 Kueue 准入和 Scheduler placement，不能直接認定缺第二張 GPU。
- 連不上服務：先核對來源、DNS、route、listener、Service endpoints 和 policy enforcement。
- Ray task pending／Slurm node 不存在：依獨立案例範圍推演，不把舊服務當成現存。

題目依據見[排障 runbook](runbooks/ai-hpc-job-troubleshooting.md)與[自動 worker 驗收](evidence/automatic-worker-20260922.json)。原證據是答案核對來源，不是要求逐字背誦。

## 7. 要實際操作雲端時

依 [平台 bootstrap](runbooks/platform-bootstrap.md)、[自動 worker](runbooks/automatic-worker.md)、[單卡訓練](runbooks/causal-lm-benchmark.md) 分別操作，不從舊快照複製指令。

操作前確認：顯式 context／namespace、資源名稱、配額、現有工作、預期副作用、回復方式、新的證據目錄。停啟 worker、提交 workload、壓測、改 NetworkPolicy、Terraform apply／destroy 都不是單純閱讀練習。

需要重跑時另存新日期／run ID，不覆寫既有 JSON、log、trace 或 source snapshot。沒有硬體／權限時可先完成本頁離線練習，不能把未跑的部分寫成通過。
