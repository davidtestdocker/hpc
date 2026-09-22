<!-- current-curriculum: 2026-09-22 -->
# Week18 Day5 — NCCL transport 排障

[上一課](<day4-kubernetes-network-troubleshooting.md>) · [本週目錄](README.md) · [下一課](<day6-gpu-nic-numa-topology.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「NCCL transport 排障」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

找不到 IB 裝置後選 Socket 可能是正常 fallback。要判斷通訊成功須看 ranks、初始化及實際 collective，不是只截一行 WARN。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[docs/demo/nccl-transport-fallback-demo.md](<../demo/nccl-transport-fallback-demo.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
從保存的 NCCL raw log 說明 transport discovery、IB 初始化失敗與 Socket fallback 的判讀。來源為 [原始單 GPU log](../../benchmark/results/week16-day4-nccl-single-gpu.txt) 與 [transport 排障紀錄](../history/20260922-before-current/week18/day5-nccl-transport-debugging.md.txt)；本輪未執行 NCCL test。

## NCCL Transport Discovery

歷史環境為 **1 GPU（NVIDIA L4）、1 rank、1 node，沒有 RDMA hardware**。紀錄中的 `NCCL_NET_PLUGIN=spcx` 使 NCCL 嘗試載入 Spectrum-X plugin；plugin library 可載入，但底層沒有可用 IB／RDMA device。

面試展示時先開 raw log，依序查看 plugin discovery、NET/IB、NET/Socket、communicator initialization，再確認 rank／node 數量。這些輸出描述 backend selection，不能單憑它們判斷跨機傳輸效能。

## Observed Log

以下逐行摘自 raw log，省略其他中間行，沒有改寫訊息：

```text
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/Plugin: Loaded net plugin SPCX (v12)
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/IB : No device found.
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Failed to initialize NET plugin SPCX
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Failed to initialize NET plugin IB
nccl-benchmark-csgjr:1:1 [0] NCCL INFO NET/Socket : Using [0]eth0:10.56.0.6<0>
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Initialized NET plugin Socket
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Assigned NET plugin Socket to comm
nccl-benchmark-csgjr:1:1 [0] NCCL INFO Using network Socket
nccl-benchmark-csgjr:1:1 [0] NCCL INFO comm 0x59e6b47a3b40 rank 0 nRanks 1 nNodes 1 localRanks 1 localRank 0 MNNVL 0
nccl-benchmark-csgjr:1:1 [0] NCCL INFO ncclCommInitRankConfig comm 0x59e6b47a3b40 rank 0 nranks 1 cudaDev 0 nvmlDev 0 busId 30 commId 0xa3c39faff10c2201 - Init COMPLETE
```
````

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從保存的 NCCL log 找初始化與 transport，解釋單 rank 沒跨節點 traffic 的原因；不要為了消除 warning 就改 host driver 或 RDMA 設定。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '5,28p' 'docs/demo/nccl-transport-fallback-demo.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/network-policy-validation-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week18/day5-nccl-transport-debugging.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
