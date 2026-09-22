<!-- readable-curriculum: 2026-09-22 -->
# Week16 Day5 — Distributed scaling

[上一課](<day4-nccl-communication-benchmark.md>) · [本週目錄](README.md) · [下一週](../week17/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

總 batch 與每 rank batch 關係會改變運算量；同機 CPU workers 共享核心與記憶體，增加 workers 可能更慢。profiler 可找同步開銷，但控制條件先要成立。

## 在現在的專案中

現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

本課對照：[runtime/pytorch/distributed_scaling.py](<../../runtime/pytorch/distributed_scaling.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
from torch.utils.data.distributed import DistributedSampler


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    # torchrun provides distributed environment variables.
    # os.environ.get 讀取 torchrun 提供的環境變數；int 把字串轉成整數。
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    distributed = world_size > 1

    use_cuda = torch.cuda.is_available()

    if distributed:
        # 條件運算式 A if 條件 else B：GPU 選 NCCL，CPU 選 Gloo。
        backend = "nccl" if use_cuda else "gloo"
        # 初始化分散式通訊群組；torchrun 提供 rank、world size 與 rendezvous 環境。
        dist.init_process_group(backend=backend)

    rank = dist.get_rank() if distributed else 0

    if use_cuda:
        # 把本程序綁到 local_rank 對應的 GPU，避免同節點所有程序使用同一張卡。
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week16/day5-distributed-training-scaling.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：CPU／Gloo DDP、單 rank NCCL 與新單 L4 訓練是不同證據，未驗證多 GPU／RDMA scaling。
> **閱讀順序**：先學本文基礎，再讀[Week16 現行對照與檢核](../learning-guide.md#week16)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week16 Day5 — Distributed Training Scaling

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/pytorch-runtime/templates/distributed-scaling-job.yaml](../../helm/pytorch-runtime/templates/distributed-scaling-job.yaml)
- [helm/pytorch-runtime/values.yaml](../../helm/pytorch-runtime/values.yaml)
- [kustomize/overlays/gpu-sg/kustomization.yaml](../../kustomize/overlays/gpu-sg/kustomization.yaml)
- [runtime/pytorch/distributed_scaling.py](../../runtime/pytorch/distributed_scaling.py)：分散式訓練擴展性量測

---

## 今日成果

建立正式 distributed scaling workload：

```text
runtime/pytorch/distributed_scaling.py
```

整合進既有：

```text
Helm
→ Kustomize
→ ArgoCD
→ Kubernetes Job
→ torchrun
→ PyTorch DDP
→ Gloo
```

目標：

```text
比較 1 worker 與 2 workers 的 Training Throughput
→ 計算 Speedup
→ 計算 Scaling Efficiency
```

---

## Scaling 指標

### Speedup

```text
Speedup
= N-worker Throughput / 1-worker Throughput
```

### Scaling Efficiency

```text
Scaling Efficiency
= Speedup / Worker 數
```

---

## Benchmark Workload

使用：

```text
PyTorch
torchrun
DistributedDataParallel
DistributedSampler
Gloo
```

目前因 GPU quota 只有 1 張 L4，因此本日採：

```text
CPU + Gloo
```

做真實 distributed scaling 驗證。

Worker 數由 Helm 控制：

```yaml
distributedScaling:
  workers: 1
```

實際啟動：

```bash
torchrun \
  --standalone \
  --nproc-per-node=1 \
  /runtime/distributed_scaling.py
```

2 workers：

```yaml
distributedScaling:
  workers: 2
```

等同：

```bash
torchrun \
  --standalone \
  --nproc-per-node=2 \
  /runtime/distributed_scaling.py
```

---

## Kubernetes Resource 設定

### 1 Worker

```yaml
workers: 1
cpuRequest: "2"
cpuLimit: "2"
```

### 2 Workers

最初設定：

```yaml
cpuRequest: "4"
cpuLimit: "4"
```

因 GKE node 雖為 4 vCPU，但 Kubernetes 可排程資源需扣除 system workload，Pod 發生：

```text
Insufficient cpu
```

最後調整為：

```yaml
workers: 2
cpuRequest: "2"
cpuLimit: "4"
```

重要觀念：

```text
CPU Capacity
≠
Kubernetes 可直接全部 Request 的 CPU

request
→ Scheduler 必須保證的資源

limit
→ Container 最多能使用的資源
```

---

## 真實 Benchmark 結果

### 1 Worker

```text
backend=gloo
device=cpu
workers=1
samples=400000
duration=68.802s
throughput=5813.76 samples/s
```

### 2 Workers

```text
backend=gloo
device=cpu
workers=2
samples=400000
duration=72.073s
throughput=5549.91 samples/s
```

---

## Scaling Analysis

```text
Speedup
= 5549.91 / 5813.76
≈ 0.955x
```

```text
Scaling Efficiency
= 0.955 / 2
≈ 47.7%
```

結果：

```text
1 Worker → 5813.76 samples/s
2 Workers → 5549.91 samples/s

Speedup → 0.955x
Efficiency → 47.7%
```

2 workers throughput 反而下降約：

```text
4.5%
```

屬於：

```text
Negative Scaling
```

---

## 為什麼增加 Worker 反而變慢

目前 2 workers 仍位於同一個 4-vCPU Node：

```text
Worker 0
   ↕
Gloo Gradient Synchronization
   ↕
Worker 1
```

兩個 process 共享：

```text
CPU
Memory Bandwidth
Node Resources
```

同時增加：

```text
Process Coordination
Gradient Synchronization
Communication Overhead
Context Switching
```

當這些 overhead 大於 parallel compute 帶來的收益時：

```text
Worker ↑
但 Throughput ↓
```

因此增加 worker 不代表一定會得到線性效能提升。

`torchrun` 本次也自動設定：

```text
OMP_NUM_THREADS=1
```

避免多 process 過度使用 CPU threads。

---

## 本日結論

```text
Distributed Scaling 必須實測
不能假設 Worker 越多一定越快
```

目前實測：

```text
CPU / Gloo
1 → 2 Workers
Speedup = 0.955x
Scaling Efficiency = 47.7%
```

這組結果將直接作為 Day6 Communication Bottleneck Analysis 的分析案例。

GPU/NCCL scaling 尚未實測，需等待至少 2 張 GPU。

---

## Quick Review

```text
Throughput
→ 每秒處理多少 Samples

Speedup
→ N Workers 相對 1 Worker 快幾倍

Scaling Efficiency
→ 實際 Speedup 距離理想線性 Scaling 多近

Negative Scaling
→ 增加 Worker 後反而變慢
```

---

## Interview Review

### Q1：為什麼增加 DDP Worker 不一定會提升 Throughput？

因為 Worker 增加後也會增加 gradient synchronization、process coordination 與 resource contention；若 communication overhead 大於 parallel compute 收益，就會出現 negative scaling。

### Q2：本次 1→2 Workers 的 Scaling 結果如何？

Throughput 從 5813.76 降至 5549.91 samples/s，Speedup 約 0.955x，Scaling Efficiency 約 47.7%，屬於 negative scaling。
