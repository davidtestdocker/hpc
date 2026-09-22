# Week19 — 准入與工作群組：Kueue／JobSet

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week18](../week18/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
