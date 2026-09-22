# Week15 — 模型 runtime 與現行單卡訓練

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week14](../week14/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

訓練包含 forward、loss、backward、optimizer update；推論不更新參數，重點常是 TTFT、TPOT、吞吐與併發。不能把推論分數當成訓練速度。

現行實驗是 13M 隨機初始化 causal LM，256 個 byte vocabulary、causal mask、next-byte targets。Batch 8／16 各三次交錯執行，20 warmup、40 measured steps；計時後另做 profiler。

runtime abstraction 是程式接口設計，不代表所有 adapter 都已接到平台 API。現在訓練由獨立 runner 建 Pod、保存證據；MPI API 只處理其 CPU rank smoke 主線。

## 目前環境與實測邊界

單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

[本週實作／證據入口](<../../benchmark/results/causal-lm-20260922/evidence.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：PyTorch GPU runtime](<Day1—PyTorch-GPU-Runtime.md>)
- [Day2：現行 causal LM 訓練](<Day2-PyTorch-Training-Runtime.md>)
- [Day3：vLLM inference](<Day3-vLLM-Inference-Runtime.md>)
- [Day4：Runtime abstraction](<Day4-Runtime-Abstraction.md>)
- [Day5：Benchmark engine](<Day5-Benchmark-Engine.md>)
- [Day6：Performance analyzer](<Day6-Performance-Analyzer.md>)
- [Day7：現行 runtime 整合範圍](<Day7-AI-Runtime-Platform-v1-Integration.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
