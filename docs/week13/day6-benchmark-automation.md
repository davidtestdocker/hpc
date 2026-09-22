<!-- readable-curriculum: 2026-09-22 -->
# Week13 Day6 — 測試自動化

[上一課](<day5-resource-monitoring.md>) · [本週目錄](README.md) · [下一課](<day7-1-cpu-benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

runner 編排環境、等待、收檔與清理，benchmark 才執行量測，analyzer 再核對及彙整。失敗時保留診斷資料，比只印 PASS／FAIL 更能追查。

## 在現在的專案中

Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

本課對照：[scripts/run_causal_lm_benchmark.py](<../../scripts/run_causal_lm_benchmark.py>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```python
def run(context, name, output):
    """用明確 context 和唯一名稱執行一次實驗；失敗時保留現場供排查。"""
    # exist_ok=False 防止重跑覆寫舊證據；目錄建立後即保存本次輸入。
    output.mkdir(parents=True, exist_ok=False)
    base = ['kubectl', '--context', context, '--request-timeout=30s', '-n', 'hpc-platform-dev']

    def kubectl(args, data=None):
        """以參數陣列呼叫 kubectl；可用 stdin 傳 manifest，失敗立即拋出例外。"""
        return subprocess.check_output(base + args, input=data, timeout=90)

    # corpus 和程式可能日後改動，因此本次快照與現行原始碼分開保存。
    source = (ROOT / 'benchmark/gpu/causal_lm_benchmark.py').read_text()
    corpus = (ROOT / 'README.md').read_text()
    (output / 'corpus.txt').write_text(corpus)
    (output / 'benchmark-source.py').write_text(source)
    cm = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': name},
          'data': {'causal_lm_benchmark.py': source, 'corpus.txt': corpus}}
    # nodeSelector 決定 GPU pool；toleration 允許接受 GPU taint。
    # nvidia.com/gpu=1 在此叢集是一個 time-sharing share，不是額外建立一張 GPU。
    # 成功後 sleep 保留容器供 exec 取檔；emptyDir 隨 Pod 刪除，必須先收回結果。
    pod = {'apiVersion': 'v1', 'kind': 'Pod', 'metadata': {'name': name,
           'labels': {'app': 'causal-lm-benchmark'}}, 'spec': {
        'restartPolicy': 'Never', 'activeDeadlineSeconds': 1200,
        'nodeSelector': {'cloud.google.com/gke-nodepool': 'gpu-pool'},
```

## 已有結果與解讀

### 單 L4 訓練：已保存的實測數據

日期：2026-09-22；環境：GKE hpc-gpu-sg、單 NVIDIA L4、PyTorch 2.12.0+cu126。模型為 13M causal LM、byte tokenizer，不是 pretrained 大模型。20 warmup、40 measured steps，各 batch 三次交錯量測。

| Batch | 次數 | Mean byte tokens/s | Mean step ms | Peak allocated MiB | Throughput CV |
|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 110,785 | 18.50 | 375.02 | 3.21% |
| 16 | 3 | 200,841 | 20.39 | 532.39 | 0.42% |

結果：吞吐 **+81.29%**，每步時間 **+10.25%**，顯存峰值 **+41.96%**。每步工作量加倍，所以不是「每步變快」，也不能推出模型品質更好。

另做的五步 CUDA profiling：batch 8／16 的 multi-tensor kernel 累積時間約 21.71／21.72 ms，GEMM 約 12.27／23.84 ms。這支持每步固定 optimizer 成本被較大 batch 攤薄的推論；kernel 時間總和不是 wall time，也不直接證明 compute-bound 或 memory-bound。

你不需要再跑 GPU：[保存的摘要](<../../benchmark/results/causal-lm-20260922/summary.json>)、[原始逐步數據](<../../benchmark/results/causal-lm-20260922/result.json>)、[完整解讀與限制](<../performance/causal-lm-l4-20260922.md>)已足夠直接閱讀。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week13/day6-benchmark-automation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：最新訓練有暖機、交錯重複量測與分析；獨立 runner 未接 MPI API，API 非 MPI 分支仍為模擬。
> **閱讀順序**：先學本文基礎，再讀[Week13 現行對照與檢核](../learning-guide.md#week13)及[對應現行入口](../performance/causal-lm-l4-20260922.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week13 Day6 - Benchmark Automation Framework

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [benchmark/postgres/run_pgbench.sh](../../benchmark/postgres/run_pgbench.sh)：PostgreSQL 壓測
- [k8s/postgres-service.yaml](../../k8s/postgres-service.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)

---

## 今天平台增加了什麼？

今天將 PostgreSQL Benchmark 流程從手動操作改造成可重複執行的 Benchmark Runner。

之前執行方式：

```
kubectl exec 進入 Pod

↓

手動輸入 pgbench command

↓

複製 Terminal 結果
```

問題：

- 參數容易輸入錯誤
- 測試流程無法重複
- 結果難以保存與比較

因此建立 Benchmark Script：

```
Benchmark Script

↓

Benchmark Pod

↓

PostgreSQL Service

↓

PostgreSQL Database
```

---

# Framework Structure

目前目錄：

```
benchmark/

└── postgres/

    ├── run_pgbench.sh

    └── results/
```

---

# Benchmark Environment

## Kubernetes

Platform:

```
GKE
```

Namespace:

```
hpc-platform-dev
```

---

## Benchmark Pod

用途：

執行 PostgreSQL Benchmark Client。

包含：

```
pgbench
postgres client tools
```

確認：

```bash
which pgbench
```

結果：

```
/usr/bin/pgbench
```

---

## Target Database

Service:

```
postgres-service:5432
```

Database:

```
pgbench
```

User:

```
hpc
```

---

# Step 1 - Create Benchmark Script

建立：

```
benchmark/postgres/run_pgbench.sh
```

功能：

- 執行 PostgreSQL Benchmark
- 接收測試參數
- 保存測試結果


---

# Step 2 - Parameterized Benchmark

Script 支援：

```
./run_pgbench.sh CLIENT THREAD TRANSACTION
```

格式：

```bash
./run_pgbench.sh 10 2 100
```

代表：

|參數|說明|
|-|-|
|10|Concurrent Clients|
|2|Worker Threads|
|100|Transactions per Client|

---

## Example

執行：

```bash
./run_pgbench.sh 10 2 100
```

等同：

```bash
pgbench \
-h postgres-service \
-U hpc \
-d pgbench \
-c 10 \
-j 2 \
-t 100
```

---

# Step 3 - Execute Inside Kubernetes Pod

Benchmark Script 不在 Host 執行。

原因：

Host 沒有：

```
pgbench
```

並且無法模擬 Kubernetes Service Network。

因此：

```
Benchmark Pod

        |
        |

postgres-service

        |
        |

postgres-0
```

---

將 Script 複製到 Pod：

```bash
kubectl -n hpc-platform-dev cp \
benchmark/postgres/run_pgbench.sh \
benchmark:/tmp/run_pgbench.sh
```

---

執行：

```bash
kubectl -n hpc-platform-dev exec -it benchmark -- bash
```

---

執行 Benchmark：

```bash
/tmp/run_pgbench.sh 10 2 100
```

---

# Benchmark Result

測試：

```
Clients:
10

Threads:
2

Transactions/client:
100
```

結果：

```
number of transactions actually processed:
1000/1000


number of failed transactions:
0


latency average:
52.029 ms


tps:
192.200688
```

---

# Step 4 - Result Logging

加入 Timestamp Result Log。

每次執行：

```
run_pgbench.sh
```

會建立：

```
results/

└── pgbench_20260809_125240.log
```

內容保存：

- Transaction Result
- Latency
- TPS

---

# Benchmark Framework Flow

完成後流程：

```
User

 |

 |

Benchmark Script

 |

 |

Benchmark Pod

 |

 |

pgbench

 |

 |

PostgreSQL Service

 |

 |

PostgreSQL Database

```

---

# Design Decision

目前 Result Storage 使用 Container Filesystem。

原因：

Week13 目標：

建立 Benchmark Framework。

重點：

- Benchmark execution
- Parameter control
- Result collection


Production 等級保存：

例如：

- Persistent Volume
- Object Storage
- Database Storage

會在 Production Platform 階段處理。

---

# Performance Engineering Insight

Automation 的價值：

從：

```
手動執行測試
```

變成：

```
固定流程 Benchmark Job
```

讓測試結果：

- 可重複
- 可比較
- 可分析

這是 Performance Engineering Workflow 的基礎。

---

# Interview Questions

## Q1

為什麼 Benchmark Client 不直接在 Kubernetes Node 執行？

Answer:

因為 Benchmark Client 應該模擬實際服務環境。

在 Kubernetes 中執行可以包含：

- Service Discovery
- Cluster Network
- Pod Communication

更接近真實工作負載。

---

## Q2

為什麼需要 Benchmark Script，而不是直接執行指令？

Answer:

Script 可以固定測試流程、參數與結果保存方式，使 Benchmark 可以重複執行並進行不同版本比較。

---

# Conclusion

Day6 完成 Benchmark Automation Framework 第一版。

目前平台具備：

- PostgreSQL Benchmark Runner
- Parameterized Testing
- Kubernetes Pod Execution
- Result Logging

下一步：

Day7 將整合 Week13 Benchmark 結果，建立 Benchmark Report。
