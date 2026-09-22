# Week19 — 准入與工作群組：Kueue／JobSet

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week18](../week18/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Kueue 依 queue 配額、ResourceFlavor 與 policy 決定 workload 是否可准入。准入不是 Pod 已被排上 node；Scheduler 才處理實際 placement。

JobSet 將 launcher／worker 的 child Jobs 組成一組生命週期。priority／preemption 能調整誰先使用配額，但不會憑空增加 GPU；recovery 也要看故障政策和重試邊界。

Topology-aware admission 參考節點拓撲資訊，歷史單 node placement 證據不能推成多 node 效能。現行 CPU MPI 完成是另一筆驗收，不會改寫歷史 ContainerCreating 的結果。

## 目前環境與實測邊界

單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

[本週實作／證據入口](<../evidence/automatic-worker-20260922.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：GPU sharing models](<day1-gpu-sharing-models.md>)
- [Day2：Kueue admission](<day2-kueue-gpu-admission.md>)
- [Day3：Quota 與等待](<day3-gpu-quota-admission-queue-behavior.md>)
- [Day4：Priority 與 preemption](<day4-priority-preemption-multi-tenancy.md>)
- [Day5：JobSet 與 MPI 群組](<day5-gang-jobset-mpi.md>)
- [Day6：Topology-aware placement](<day6-topology-aware-gpu-scheduling.md>)
- [Day7：排程主線整合](<day7-gpu-scheduling-platform-integration.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
