<!-- current-curriculum: 2026-09-22 -->
# Week17 Day2 — MPI 效能測試

[上一課](<day1-mpi-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day3-hpc-communication-stack.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「MPI 效能測試」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

hello world 測 distributed launch；小訊息 latency、大訊息 bandwidth、collective scaling 是不同效能測項。沒有完整 benchmark 結果時，不能把功能 smoke 改稱性能驗收。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
# mpirun 的 -np 指定 rank 數，--host 指定主機；OMPI_COMM_WORLD_RANK 是 Open MPI 注入的程序編號。
# worker 的 & 背景執行 sshd，$! 記錄 PID；kill -0 檢查程序是否存在，wait 等待並取得退出狀態。
# /tmp/fail-worker 存在時退出 42，供故障恢復實驗使用；|| true 容忍清理時 kill 失敗。
spec:
  # 是否暫停啟動工作；Kueue 可在准入後解除暫停。
  suspend: true

  # Workers run SSH servers; launcher completion defines successful execution.
  successPolicy:
    operator: All
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
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 MPI template 實際執行的 binary，對照歷史 OSU 未完成的限制；為未來測試列明 message size、ranks、nodes 和時間單位，但本課不聲稱已做。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '19,42p' 'api/workloads/templates/jobset-mpi.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day2-mpi-performance-benchmark.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
