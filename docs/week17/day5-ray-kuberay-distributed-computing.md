<!-- current-curriculum: 2026-09-22 -->
# Week17 Day5 — Ray 與 KubeRay

[上一課](<day4-slurm-multinode-hpc-cluster.md>) · [本週目錄](README.md) · [下一課](<day6-cluster-scheduling-integration.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Ray 與 KubeRay」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

KubeRay 管理 Ray Pod，Ray scheduler 依自己的資源宣告分派 task。Pod Running 但 Ray GPU=0 時，num_gpus=1 task 仍可 pending；不同控制迴圈負責不同恢复。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[docs/demo/ray-worker-recovery-demo.md](<../demo/ray-worker-recovery-demo.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
透過兩個既有案例展示 Kubernetes、Ray scheduler 與 KubeRay controller 的責任邊界：resource mismatch，以及 worker 消失後的 task retry。本文件整理 historical evidence，供面試時依設定、症狀與結果展示；本輪未重跑實驗，也未接入主 MPI E2E。

## Failure Scenario

環境設定見 [RayCluster](../../ray-cluster.yaml)：Ray 2.47.1、namespace `ray-system`、cluster `hpc-ray`，CPU worker group 的 desired replicas 為 2。

| 案例 | Trigger | 對應實作 |
|---|---|---|
| Resource mismatch | CPU Ray cluster 上提交要求 `num_gpus=1` 的 task | [mismatch RayJob](../../ray-resource-mismatch-job.yaml) |
| Worker recovery | 長時間 task 執行中，刪除承載它的 Ray worker Pod，造成 Ray node disappearance | [recovery RayJob](../../ray-worker-recovery-job.yaml) |

這是兩個分開的案例；GPU pending task 不是後面 recovery 測試的 long_task。

## Observed Symptoms

[歷史排障紀錄](../history/20260922-before-current/week20/day5-ai-hpc-production-troubleshooting.md.txt) 與 [runbook](../runbooks/ai-hpc-job-troubleshooting.md) 保存以下觀察。Resource mismatch 時 Kubernetes Pods 為 Running，但 Ray resources 為 CPU=3、GPU=0；task 要求 CPU=1、GPU=1：

```text
{'CPU': 1.0, 'GPU': 1.0}: 1+ pending tasks/actors
```

Worker recovery 案例的 task state 摘錄：

```text
````

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 Ray mismatch／retry 案例，區分 worker Pod 重建與 task retry。保存的 retry 到 RUNNING，不把它加寫成最終 SUCCEEDED。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '5,28p' 'docs/demo/ray-worker-recovery-demo.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day5-ray-kuberay-distributed-computing.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
