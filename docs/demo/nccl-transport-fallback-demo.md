# NCCL Transport Fallback Demo

## Demo 目的

從保存的 NCCL raw log 說明 transport discovery、IB 初始化失敗與 Socket fallback 的判讀。來源為 [原始單 GPU log](../../benchmark/results/week16-day4-nccl-single-gpu.txt) 與 [transport 排障紀錄](../history/20260922-before-current/week18/day5-nccl-transport-debugging.md)；本輪未執行 NCCL test。

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

## Interpretation

| Evidence | 可支持的結論 |
|---|---|
| SPCX plugin loaded | Container 內 plugin library 可載入，不代表 RDMA hardware 存在 |
| `NET/IB : No device found` | 當次執行找不到可用 IB／RDMA device |
| SPCX／IB initialization failed | 該次 transport discovery 無法使用這些 network plugins |
| `Using network Socket` | NCCL 最後選到 Socket backend；log 顯示選用 eth0 |
| `nRanks 1 nNodes 1`、`Init COMPLETE` | 單 rank／單 node communicator 初始化成功；不是 multi-node traffic evidence |

## Fallback Path

```text
NCCL_NET_PLUGIN=spcx
→ Spectrum-X plugin loaded
→ IB／RDMA device discovery：No device found
→ SPCX／IB initialization failed
→ Socket initialized and assigned
→ Using network Socket
→ single-rank communicator Init COMPLETE
```

因此這個案例展示「plugin 存在、hardware 不可用、backend fallback 後初始化成功」的診斷鏈。Raw log 另有 single-GPU all_reduce_perf 輸出，其數值不能當作 network fabric bandwidth。

## Limitation

本案例是 transport fallback evidence，**不是 RDMA benchmark**。只有 1 GPU、1 rank、1 node，沒有 multi-node NCCL traffic 驗證。

- 沒有 RDMA hardware，也沒有 `ib_write_bw` 測量。
- 沒有 RoCE／PFC／ECN validation。
- 沒有 TCP vs RDMA performance comparison、multi-node AllReduce bandwidth 或 scaling efficiency 結果。

## 面試重點

- Plugin library 成功載入與 RDMA device 可用是不同條件，需看完整初始化鏈。
- Socket selection 是可用 backend 的選擇結果；不能只憑 IB failure 就判定整個 NCCL 初始化失敗。
- 先確認 GPU／rank／node 數量，再界定 log 能支持的 transport 與 performance 結論。
