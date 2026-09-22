# Week17 — MPI、Slurm、Ray：分散式工作不同層

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week16](../week16/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

MPI 是程序間通訊模型，rank 識別參與者；launcher 啟動程序，worker 執行程式。rank/hostname 輸出證明啟動與連線，不是 bandwidth benchmark。

Slurm 分配叢集資源並執行 batch job，Ray 排程 task／actor，Kubernetes 排程 Pod；多層並存時各有資源視圖。Kueue 准入則在工作啟動前處理 quota，不取代這些 scheduler。

主 API 使用 JobSet 管理 CPU MPI；歷史 Slurm CPU VM 和 Ray 案例獨立。主平台三個 workers 可共置一台 node，不能把三個 Pod 寫成三台實體機。

## 目前環境與實測邊界

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

[本週實作／證據入口](<../evidence/automatic-worker-20260922.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：MPI rank 與 launcher](<day1-mpi-fundamentals.md>)
- [Day2：MPI 效能測試](<day2-mpi-performance-benchmark.md>)
- [Day3：HPC communication stack](<day3-hpc-communication-stack.md>)
- [Day4：Slurm 多節點 CPU 案例](<day4-slurm-multinode-hpc-cluster.md>)
- [Day5：Ray 與 KubeRay](<day5-ray-kuberay-distributed-computing.md>)
- [Day6：排程層整合](<day6-cluster-scheduling-integration.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
