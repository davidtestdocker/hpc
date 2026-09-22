# Week14 — GPU：硬體、runtime 與排程分層

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week13](../week13/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Driver 讓作業系統與 GPU 溝通；CUDA runtime 與框架執行運算；device plugin 讓 Kubernetes 宣告 GPU 資源。這些層任何一個缺失，都可能造成「看得到資源卻跑不了運算」。

主環境一張 NVIDIA L4，time-sharing 公布多個 share，沒有把硬體變成多張卡。request 一個 share 也不等於獨占，其他工作可能影響延遲與記憶體。

GPU utilization、VRAM used、PyTorch allocated／reserved、tokens/s 不是同一指標。歷史 P100 dashboard 與新 L4 實驗必須標不同來源。

## 目前環境與實測邊界

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

[本週實作／證據入口](<../performance/causal-lm-l4-20260922.md>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day2：GPU scheduling](<day2-kubernetes-gpu-scheduling.md>)
- [Day3：GPU 監控架構](<day3-gpu-monitoring-architecture.md>)
- [Day4：GKE GPU pool](<Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md>)
- [Day5：DCGM 指標整合](<Day5-GPU-Metrics-Monitoring-integration.md>)
- [Day6：Dashboard 與實驗驗證](<Day6-gpu-dashboard-establish-and-gpuworkload-verification.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
