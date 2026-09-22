<!-- current-curriculum: 2026-09-22 -->
# Week12 Day4 — 歷史監控與時間對齊

[上一課](<Day3-Linux-Disk-Performance-Analysis.md>) · [本週目錄](README.md) · [下一課](<Day5-Linux-CPU-Benchmark-with-sysbench.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「歷史監控與時間對齊」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

單次 snapshot 無法描述整段事件；要對齊工作開始／結束、時區、取樣頻率與重啟時間。歷史資料可以證明當時觀察，不代表現在仍有同樣瓶頸。

## 在現在的專案中

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

本課對照：[docs/evidence/README.md](<../evidence/README.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
| Linux Performance | [CPU analysis](../history/20260922-before-current/week12/Day1-Linux-CPU-Performance-Analysis.md.txt)、[perf](../history/20260922-before-current/week12/Day6-Linux-CPU-Profiling-with-perf.md.txt)、[strace](../history/20260922-before-current/week12/Day7-Linux-System-Call-Analysis-with-strace.md.txt)、[CPU report](../../benchmark/cpu/results/cpu_benchmark_20260810.md) | Linux CPU／process／system-call 診斷紀錄與 stress-ng CPU saturation baseline | 歷史環境的輸出／報告；不是主 MPI job 的自動 profiling 或跨機型可直接比較的結果 |
| RBAC / Security | [API JobSet RBAC](../../k8s/security/api-jobset-rbac.yaml)、[RBAC 驗證](../history/20260922-before-current/week20/day1-rbac-serviceaccount-least-privilege.md.txt)、[Pod hardening](../history/20260922-before-current/week20/day2-pod-image-secret-security.md.txt)、[NetworkPolicy 實測](network-policy-validation-20260921.json) | API namespace-scoped JobSet 權限設定；歷史 benchmark-runner 允許／拒絕；隔離 Calico GKE ingress baseline／allow／deny／recovery | benchmark-runner 與 api-jobset-runner 是不同身份；NetworkPolicy 實測不在主 cluster，未涵蓋 egress、跨 namespace 或全平台 hardening |
| Terraform / GitOps | [Terraform 證據](terraform-gpu-sg-20260921.md)、[CPU-only bootstrap 驗收](cpu-bootstrap-acceptance-20260921.json)、[gpu-sg root](../../terraform/environments/gpu-sg/main.tf)、[歷史 GitOps 紀錄](../history/20260922-before-current/week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md.txt) | 主環境 import 零 drift；全新 CPU-only cluster 完成 controllers／Secrets／queues／平台 bootstrap、health／RBAC／PVC 驗收及銷毀 | 不涵蓋全新 GPU cluster MPI 執行；缺 remote state；Argo dev 仍指舊 overlays/dev |
| L4 Causal LM / CUDA Profiling | [9/22 報告](../performance/causal-lm-l4-20260922.md)、[原始證據與 hashes](../../benchmark/results/causal-lm-20260922/evidence.json) | 13M causal LM、文字 byte tokens、交錯三次量測、兩份 CUDA traces、同步 nvidia-smi 遙測 | 單 L4 time-sharing；非 pretrained LLM 品質或多 GPU 結論；獨立 runner 尚未接 MPI API |

## Capability Matrix

狀態是證據標記，可同時存在，不是成熟度分數：

- **Implemented**：repo 有對應程式、script 或 declarative manifest；以「範圍」欄為準。
- **Validated**：repo 保存範圍內的執行或觀察結果；本索引使用既有 evidence，未重新執行實驗。
- **Documented**：有可追溯的說明與結果入口。
- **Partial**：該列涵蓋的能力仍有未整合或未驗證部分，明列於最後一欄。

| 分類 | 範圍 | 狀態 | Partial 邊界／未完成項目 |
|---|---|---|---|
| Platform | API submission、背景 polling worker、MPI dispatch／rank execution／terminal collection | Implemented · Validated · Documented · Partial | 9/22 自動結果回收與重啟接續已驗證；仍缺 artifact storage、跨 DB／Redis 原子交易與 full lifecycle state machine |
| Distributed Compute | MPI JobSet、Ray tasks／recovery、Slurm multi-node MPI | Implemented · Validated · Documented · Partial | 各自獨立；Ray／Slurm 未接 API；Ray retry evidence 到 RUNNING，Slurm 歷史 compute VM 已移除 |
| GPU / AI Performance | 13M causal LM training／CUDA profiling、歷史 DDP／vLLM／NCCL | Implemented · Validated · Documented · Partial | 單 L4 time-sharing、byte corpus；無 pretrained LLM 品質、multi-node GPU scaling／RDMA 結論 |
| Scheduling | Kueue queue／quota／priority／preemption／TAS | Implemented · Validated · Documented · Partial | 單實體 GPU node 的 quota／placement 實驗；無 multi-node／cross-zone TAS 驗證 |
| Observability | API metrics、Prometheus／Grafana／DCGM 設定與歷史監控 | Implemented · Validated · Documented · Partial | 缺主 E2E per-job metrics／result 關聯；舊 P100 dashboard evidence 與目前 L4 分開 |
| Infrastructure | Terraform、bootstrap、Helm、Kustomize、Argo CD | Implemented · Validated · Documented · Partial | 全新 CPU-only cluster 已完成 Terraform、controllers、queues、Secrets、platform apply／acceptance／destroy；Spot GPU rehearsal 被全域 quota 阻擋並清理，尚缺全新 GPU MPI 執行、remote state 與 Argo CD 對齊 |
| Security | Namespace RBAC、Pod hardening、NetworkPolicy manifests | Implemented · Validated · Documented · Partial | 隔離 Calico GKE 已驗證 ingress packet allow／deny／recovery；主 cluster enforcement、egress／跨 namespace 與全平台 hardening未完成 |
| Troubleshooting | Kueue、JobSet、Ray、Slurm、NCCL failure-domain 定位 | Implemented · Validated · Documented · Partial | 有 failure scripts／hooks 與紀錄；單 GPU node 無 node failover，Slurm 未驗證恢復，非完整 HA 認證 |
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀證據索引中的 Linux 與監控條目，為一個結果標出環境、時間與 workload；缺欄位時明說缺失，不補猜測數字。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '94,117p' 'docs/evidence/README.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../../benchmark/cpu/results/cpu_benchmark_20260810.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week12/Day4-Linux-Historical-Performance-Analysis.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
