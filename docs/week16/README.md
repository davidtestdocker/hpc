# Week16 — 分散式訓練：process、device 與通訊

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week15](../week15/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
