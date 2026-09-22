# Week16 — 分散式訓練：process、device 與通訊

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week15](../week15/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

rank 是通訊群組中的程序編號，world size 是程序數，local rank 常用於選本節點裝置。增加程序不等於增加實體 GPU，一張卡上不可直接把 local_rank=1 當第二張卡。

DDP 各程序保有模型副本，分資料做計算並同步梯度。CPU Gloo 可學流程；GPU NCCL 測的是另一種裝置與通訊路徑。通訊開銷、資料切分與 batch 定義會影響 scaling。

speedup=T1/TN，效率可用 speedup/N 描述，但前提是工作量可比。固定總工作量與固定每 worker 工作量是不同問題，不能用多做的工作量冒充縮短相同工作時間。

## 目前環境與實測邊界

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

[本週實作／證據入口](<../evidence/README.md>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：多 GPU 基本概念與單卡限制](<day1-multi-gpu-fundamentals.md>)
- [Day2：CPU／Gloo DDP](<day2-pytorch-ddp.md>)
- [Day3：NCCL collective](<day3-nccl-fundamentals.md>)
- [Day4：NCCL benchmark 邊界](<day4-nccl-communication-benchmark.md>)
- [Day5：Distributed scaling](<day5-distributed-training-scaling.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
