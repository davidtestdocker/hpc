<!-- current-curriculum: 2026-09-22 -->
# Week19 Day5 — JobSet 與 MPI 群組

[上一課](<day4-priority-preemption-multi-tenancy.md>) · [本週目錄](README.md) · [下一課](<day6-topology-aware-gpu-scheduling.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「JobSet 與 MPI 群組」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

launcher 和 workers 分別是 replicatedJobs，JobSet 管理整組狀態。群組生命週期不等於所有 Pod 在同一瞬間開始，也不等於任意失敗都可無成本重跑。

## 在現在的專案中

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
    targetReplicatedJobs:
      - launcher

  # 工作失敗時由控制器採用的處理策略。
  failurePolicy:
    # JobSet 層級允許的重新啟動次數上限。
    maxRestarts: 1
    restartStrategy: Recreate
    # 規則清單；RBAC 中定義 API 存取權限，Ingress 中定義路由。
    rules:
      - name: restart_on_child_job_failure
        action: RestartJobSet

  network:
    enableDNSHostnames: true

  # JobSet 管理的子 Job 群組，例如 launcher 與 worker。
  replicatedJobs:
    - name: launcher
      # 期望副本數；設定為 0 表示不維持執行中的副本。
      replicas: 1
      # 子物件模板；控制器以此內容建立 Pod 或相關工作資源。
      template:
        spec:
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 replicatedJobs、failurePolicy、mpirun 命令，解釋固定 job 名與 owner label 怎麼協助 worker 接回提交結果。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '29,52p' 'api/workloads/templates/jobset-mpi.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week19/day5-gang-jobset-mpi.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
