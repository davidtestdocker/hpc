<!-- current-curriculum: 2026-09-22 -->
# Week16 Day4 — NCCL benchmark 邊界

[上一課](<day3-nccl-fundamentals.md>) · [本週目錄](README.md) · [下一課](<day5-distributed-training-scaling.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「NCCL benchmark 邊界」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

all-reduce benchmark 需交代 rank 數、訊息大小、裝置與鏈路；單 rank 數字不能當 inter-node bandwidth。algbw 與 busbw 也有不同定義，不能混報。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[benchmark/results/week16-day4-nccl-single-gpu.txt](<../../benchmark/results/week16-day4-nccl-single-gpu.txt>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
=== Clone nccl-tests ===
Cloning into '/opt/nccl-tests'...
=== Build nccl-tests ===
make -C src build BUILDDIR=/opt/nccl-tests/build
make[1]: Entering directory '/opt/nccl-tests/src'
make[2]: Entering directory '/opt/nccl-tests/os'
Compiling  timer.cc                            > /opt/nccl-tests/build/timer.o
Compiling /opt/nccl-tests/build/verifiable/verifiable.o
Compiling  all_reduce.cu                       > /opt/nccl-tests/build/all_reduce.o
Compiling  linux.cc                            > /opt/nccl-tests/build/os/linux.o
Compiling  common.cu                           > /opt/nccl-tests/build/common.o
Creating archive /opt/nccl-tests/build/os/linux.o    > /opt/nccl-tests/build/os/libnccl_test_os.a
make[2]: Leaving directory '/opt/nccl-tests/os'
Compiling  util.cu                             > /opt/nccl-tests/build/util.o
Compiling  all_gather.cu                       > /opt/nccl-tests/build/all_gather.o
Compiling  broadcast.cu                        > /opt/nccl-tests/build/broadcast.o
Compiling  reduce_scatter.cu                   > /opt/nccl-tests/build/reduce_scatter.o
Compiling  reduce.cu                           > /opt/nccl-tests/build/reduce.o
Compiling  alltoall.cu                         > /opt/nccl-tests/build/alltoall.o
Compiling  alltoallv.cu                        > /opt/nccl-tests/build/alltoallv.o
Compiling  scatter.cu                          > /opt/nccl-tests/build/scatter.o
Compiling  gather.cu                           > /opt/nccl-tests/build/gather.o
Compiling  sendrecv.cu                         > /opt/nccl-tests/build/sendrecv.o
Compiling  hypercube.cu                        > /opt/nccl-tests/build/hypercube.o
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 核對保存的單 GPU log 中 rank／device 資訊，將可證明的初始化與不能證明的 RDMA／多卡速度寫成兩欄。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '1,24p' 'benchmark/results/week16-day4-nccl-single-gpu.txt'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week16/day4-nccl-communication-benchmark.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
