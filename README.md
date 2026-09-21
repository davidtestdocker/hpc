# Week1～Week20 學習總覽

從 Linux 與 Python 基礎出發，逐步學習容器化、平台開發、雲端部署、效能分析，以及 HPC／AI 分散式運算與排障。下表依各週學習文件整理；點選週次可查看完整筆記與實驗紀錄。表中的概念學習與歷史實作不代表目前平台已全面整合，實際驗證範圍見後續平台介紹與 [Evidence Index](docs/evidence/README.md)。

| 週次 | 學習主題 | 學習內容與能力 | 技能／技術 |
|---|---|---|---|
| [Week1](docs/week1/) | Linux 系統基礎 | 理解程序、CPU 排程、上下文切換、記憶體與磁碟 I/O；建立逐層定位效能瓶頸的思路 | Linux、Process／PID、Scheduler、Context Switch、top、ps、free、iostat |
| [Week2](docs/week2/) | Python 與系統資訊收集 | 使用變數、函式與回傳值組織程式，以資料結構表示程序資訊；執行 Linux 指令並取得輸出 | Python、Function、return、List、Dictionary、subprocess、stdout |
| [Week3](docs/week3/) | Docker 容器化 | 安裝 Docker、區分 Image 與 Container；建置監控程式映像、管理容器生命週期，理解 namespace 隔離 | Docker Engine、Dockerfile、Image、Container、Docker Compose、Namespace |
| [Week4](docs/week4/) | 平台 API 與工作佇列 | 設計工作提交與查詢 API、Job ID 與記憶體佇列；整合容器設定、健康檢查、日誌與基本指標 | FastAPI、Uvicorn、REST API、Pydantic、OpenAPI、Producer／Consumer、Docker Compose |
| [Week5](docs/week5/) | 工作狀態與資料持久化 | 將狀態移至 Redis，學習持久化、worker 狀態轉移、逾時恢復與重試上限；以 PostgreSQL 保存 metadata | Redis、RDB／AOF、Processing Queue、Retry、Dead Letter Queue、PostgreSQL、SQLAlchemy ORM |
| [Week6](docs/week6/) | Kubernetes 平台部署 | 理解控制器與服務探索；建立 K3s 環境，部署 API、Redis、PostgreSQL，串接服務與持久化儲存 | Kubernetes、K3s、Pod、Deployment、ReplicaSet、Service、Namespace、StatefulSet、PVC |
| [Week7](docs/week7/) | Kubernetes 服務管理 | 分離設定與敏感資訊、配置資源與健康探針；建立對外路由，透過負載測試觀察 HPA 擴容 | ConfigMap、Secret、Requests／Limits、QoS、Probes、NodePort、Ingress／Traefik、HPA、k6 |
| [Week8](docs/week8/) | GitOps 與多環境部署 | 學習宣告式同步，將服務封裝為 Helm Charts；管理 release／rollback，整合 dev／stage／prod 設定與部署 | GitOps、Argo CD、Helm、Values／Templates、Release、Kustomize Base／Overlay、Reconciliation |
| [Week9](docs/week9/) | Infrastructure as Code | 管理雲端資源生命週期、state 與 module 重構；串接 VM、網路、防火牆及多環境設定，建立 GKE 與 Node Pool | Terraform、HCL、Provider、Plan／Apply、State Migration、Module／Output、GCP VPC、GKE |
| [Week10](docs/week10/) | CI/CD 與自動化測試 | 建立語法、品質與 API 測試流程，以 mock 隔離外部依賴；串接映像建置、推送與 GitOps 部署更新 | GitHub Actions、Ruff、Pytest、TestClient、Fixture／Monkeypatch、Docker Build、Artifact Registry、Argo CD |
| [Week11](docs/week11/) | 平台可觀測性 | 建立監控 Node Pool，理解 pull model 與 target 狀態；收集 API／Node 指標，整合自動探索與儀表板 | Prometheus、Scrape Job／Target、FastAPI Instrumentator、Node Exporter、Grafana、Kubernetes Service Discovery、RBAC |
| [Week12](docs/week12/) | Linux 效能診斷 | 分析 CPU、記憶體、磁碟與歷史負載；建立 CPU baseline，透過 profiling 與 system call 追蹤定位瓶頸 | top、mpstat、pidstat、vmstat、iostat、sar／sysstat、fio、sysbench、perf、strace |
| [Week13](docs/week13/) | Benchmark 與結果整合 | 量測 API、Redis、資料庫、CPU、儲存與網路；比較併發、吞吐與延遲，整合資源觀察、PASS／FAIL 與結果保存 | ApacheBench、redis-benchmark、pgbench、stress-ng、fio、iperf3、kubectl top、Shell、tee／pipefail |
| [Week14](docs/week14/) | GPU 排程與監控 | 理解 GPU 資源宣告與 Pending 原因，建立 GKE GPU Node Pool；執行 CUDA workload，觀察 GPU 使用率、顯存與溫度 | NVIDIA Device Plugin、nvidia.com/gpu、Taints／Tolerations、CUDA、nvidia-smi、DCGM Exporter、Prometheus、Grafana |
| [Week15](docs/week15/) | AI Runtime 與推論效能 | 執行 PyTorch 訓練與 vLLM 推論，建立 runtime adapter；以 concurrency benchmark 與 JSON 結果分析吞吐和延遲取捨 | PyTorch、DataLoader、CUDA、vLLM、Runtime Abstraction、Continuous Batching、KV／Prefix Cache、TTFT／TPOT／ITL |
| [Week16](docs/week16/) | 分散式訓練與通訊效能 | 理解 rank、rendezvous 與梯度同步；實作 CPU／Gloo DDP，分析 1→2 workers scaling，進行單 GPU NCCL 測試 | torchrun、PyTorch DDP、Gloo、RANK／WORLD_SIZE、AllReduce、NCCL、nccl-tests、Speedup／Scaling Efficiency |
| [Week17](docs/week17/) | HPC 分散式運算與排程 | 實作 MPI 通訊與單節點 OSU 測試、Slurm CPU 多節點 MPI、Ray tasks／actors；比較排程層次，理解 RDMA 通訊架構與硬體需求 | Open MPI、OSU Micro-Benchmarks、Slurm、MUNGE、Ray／KubeRay、RayJob；RDMA／RoCE／InfiniBand 概念 |
| [Week18](docs/week18/) | 網路與分散式通訊排障 | 建立頻寬、延遲、丟包與 MTU 基線；從封包追查連線故障，逐層檢查 Kubernetes 網路、NCCL Socket fallback 與 GPU／NIC／NUMA locality | ip／ss、ping、iperf3、tcpdump、iptables、ethtool、DNS／EndpointSlice、NCCL Debug、PCIe／NUMA |
| [Week19](docs/week19/) | GPU 共享與工作准入 | 比較 GPU 共享模式，實驗 time-slicing、quota、priority／preemption；整合 JobSet MPI，驗證單 GPU node 的 TAS placement | Time-Slicing、MPS／MIG 概念、Kueue、ResourceFlavor、ClusterQueue／LocalQueue、PriorityClass、JobSet、TAS |
| [Week20](docs/week20/) | 安全、故障恢復與技術選型 | 實作最小權限與 Pod hardening、NetworkPolicy 設計／schema 驗證；分析 JobSet recovery、Ray retry、Slurm node failure，整理跨層排障與架構選型 | RBAC／ServiceAccount、SecurityContext、Image／Secret Security、NetworkPolicy、FailurePolicy、Runbook；OpenStack／HTCondor／LSF／DLRover 概念 |

這 20 週的學習逐步形成下方的 **HPC AI Performance Engineering Platform**：以 API、佇列與 Kubernetes 工作執行為主線，搭配監控、效能實驗及故障排查案例。以下說明整合後的平台架構、主要 demo、可追溯成果與目前限制。

---

# HPC AI Performance Engineering Platform

## Overview

以 API 驅動 distributed HPC／AI workload submission、scheduling 與 execution，結合 observability、performance analysis 和 failure troubleshooting 的工程作品。

主展示是 FastAPI → Redis queue → Kubernetes JobSet／Kueue → MPI ranks；Ray、Slurm、NCCL 與效能實驗提供平行的 supporting evidence。作品對應 HPC AI Performance、GPU Platform、AI Infrastructure 與 Platform Engineering，已完成工作提交與 rank execution，尚未形成完整 benchmark lifecycle 閉環。

## Architecture

```mermaid
flowchart LR
    C["Client"] --> A["FastAPI"]
    A --> D["PostgreSQL: initial metadata"]
    A --> R["Redis: job state / queue"]
    R --> W["Worker / Dispatcher"]
    W --> K["Kubernetes API"]
    K --> J["JobSet"]
    J --> Q["Kueue admission"]
    Q --> M["MPI launcher + workers"]
```

Worker 目前由 `POST /worker/process-next` 手動觸發。Kueue 處理 queue／quota／TAS admission；JobSet 管理 distributed job grouping；admission 後由 Kubernetes Scheduler 完成 Pod placement。PostgreSQL 保存初始 metadata，後續 job state 目前在 Redis。

完整分工與 Node Pool 邊界見 [Final Architecture](docs/architecture/platform-architecture.md)。

## Main Demo

`POST /benchmark` → Redis queue → worker dispatch → 動態 `mpi-<job_id>` JobSet → Kueue admission → 1 launcher + 3 workers → 3 MPI ranks。

已保存成功 JobSet `mpi-52eedc2a-f6b1-4c97-9c11-529223ed6899` 與 rank 0／1／2 輸出。這是 GPU node pool 上的 CPU MPI execution demo，不能等同 multi-node GPU benchmark。

- [End-to-End MPI JobSet Demo](docs/demo/end-to-end-mpi-jobset-demo.md)：前置條件、操作與成功 evidence。
- [Platform Demo Script](docs/demo/platform-demo-script.md)：展示順序。

## Core Capabilities

| 領域 | 已有能力與範圍 |
|---|---|
| Platform / API | FastAPI submission／query、PostgreSQL initial metadata、Redis queue／retry／dead-letter、MPI dispatch |
| Distributed Compute | MPI JobSet 主線；獨立 Ray／KubeRay tasks 與 Slurm CPU multi-node MPI experiments |
| GPU / AI Performance | vLLM concurrency analysis、PyTorch runtime／CPU DDP profiling、單 GPU NCCL transport evidence |
| Scheduling | Kueue queue／quota／ResourceFlavor、priority／preemption、單 GPU node TAS placement |
| Observability | API metrics、Prometheus／Grafana／DCGM manifests 與歷史驗證 |
| Infrastructure | GKE、Helm／Kustomize、Terraform／Argo CD 部署成果；新舊環境尚待對齊 |
| Security | Namespace ServiceAccount／RBAC、Pod hardening experiments、NetworkPolicy design／schema validation |
| Troubleshooting | Admission、placement、runtime resource mismatch、worker failure、Slurm node failure、NCCL fallback |

## Supporting Demos

以下是平行案例，不是 MPI 執行後自動串接的 pipeline；Ray／Slurm 尚未接入主 API。

- [Ray Worker Recovery](docs/demo/ray-worker-recovery-demo.md)：resource mismatch、NODE_DIED retry 與 KubeRay reconciliation。
- [Slurm Failure Troubleshooting](docs/demo/slurm-failure-troubleshooting-demo.md)：成功 CPU multi-node MPI baseline 與 PENDING／node failure 根因定位。
- [NCCL Transport Fallback](docs/demo/nccl-transport-fallback-demo.md)：IB 不可用後選用 Socket，單 rank 初始化 evidence。
- [JobSet Recovery](docs/demo/jobset-recovery-demo.md)：歷史 mpi-real exit 42、整組 Recreate、JobsReady 與 Kueue admission blockage。

## Performance

固定 128 requests 的 vLLM 結果中，concurrency 16／32／64 的 throughput 為 **16.748／24.988／32.379 req/s**；mean TTFT 為 **135.601／188.663／448.579 ms**。32 → 64 的 throughput 增加 29.6%，TTFT 增加 137.8%，呈現此 workload 的 latency tradeoff。

另保存 stress-ng CPU saturation、fio ephemeral-storage baseline、同 node iperf3、CPU／Gloo DDP profiling、單 GPU NCCL fallback，以及歷史 P100 DCGM dashboard evidence。它們來自不同環境，未由主 E2E 自動回收。

詳見 [Performance Report](docs/performance/performance-report.md)，包含數據來源、測試方法與限制。

## Infrastructure

主 E2E 使用 GKE `hpc-gpu-sg`、namespace `hpc-platform-dev`：`system-pool` 承載 CPU platform／control workloads，`gpu-pool` 提供 NVIDIA L4 distributed／GPU workload 資源。Node Pool 不等於單一 node，現有 platform overlay 也未以 nodeSelector 明確鎖定 system-pool。

[Helm](helm/) 與 [platform Kustomize overlay](kustomize/overlays/gpu-sg-platform/) 保存服務與 API RBAC。現有 [Terraform dev](terraform/environments/dev/main.tf) 定義 hpc-dev，[Argo CD dev](argocd/application-dev.yaml) 指向舊 overlays/dev；**hpc-gpu-sg 主 E2E 與舊 IaC／GitOps environment 尚未完全對齊**。

## Security

API 使用 [api-jobset-runner ServiceAccount／namespace RBAC](k8s/security/api-jobset-rbac.yaml)，以 least privilege 限制 JobSet 操作。另有 [Pod hardening 紀錄](docs/week20/day2-pod-image-secret-security.md) 與 [NetworkPolicy 設計](docs/week20/day3-networkpolicy-tenant-isolation.md)；後者僅驗證 schema，未驗證 packet deny enforcement。SSH private keys 不放入 repo。

## Evidence

[Evidence Index / Capability Matrix](docs/evidence/README.md) 將 15 項能力對應到真實 scripts、manifests、JSON／log 與 historical records，逐項標示 verified scope 和 limitation。歷史結果不代表目前 cluster 即時狀態。

## Current Boundary

**已完成：** API submission → queue → dispatch → Kueue admission → MPI ranks。

**尚未完成：** automatic worker daemon、JobSet completion watcher、Kubernetes final status → API／DB sync、result collector、full lifecycle state machine。MPI job API 目前停在 `submitted`；其他 benchmark 分支仍可能 simulated。既有 rank demo 不等於完整 production-ready benchmark system。

## Repository Structure

```text
api/          FastAPI、database、MPI renderer／dispatcher
benchmark/    Benchmark scripts 與保存結果
runtime/      PyTorch／vLLM runtime adapters
k8s/          Scheduling、security、workload manifests
helm/         Service／runtime／monitoring charts
kustomize/    Deployment overlays
terraform/    Infrastructure modules 與 environments
analysis/     Performance analyzer
docs/        Architecture、demos、evidence、reports、歷史紀錄
```

## Demo Quick Start

1. 先完成 [Demo prerequisite](docs/demo/end-to-end-mpi-jobset-demo.md)：確認 cluster context、namespace、平台服務、JobSet／Kueue／queues、SSH Secret 與 DB init。此處假設平台已部署且可用，完整設定見該文件。
2. 另開 terminal 保持 API port-forward：

```bash
kubectl port-forward -n hpc-platform-dev service/api-service 8000:8000
```

3. 提交 MPI 工作，記下回傳的 `job_id`：

```bash
curl -sS -X POST http://127.0.0.1:8000/benchmark \
  -H 'Content-Type: application/json' -d '{"benchmark":"mpi"}'
```

4. 觸發 worker，確認回傳 `job_id` 與 `result.jobset_name` 對應本次工作。此 endpoint 取 queue 中下一筆，若有其他 pending jobs，可能先處理它們。

```bash
curl -sS -X POST http://127.0.0.1:8000/worker/process-next
```

5. 將下面 placeholder 替換為本次回傳的 JobSet name，查看 admission 後是否 `SUSPENDED=false`：

```bash
MPI_JOBSET='mpi-<job_id>'
kubectl get jobset "$MPI_JOBSET" -n hpc-platform-dev
```

6. Launcher 啟動後查看該 child Job 的 log，確認 rank 0／1／2：

```bash
kubectl logs -n hpc-platform-dev "job/${MPI_JOBSET}-launcher-0" -c launcher
```

## Limitations / Future Improvements

後續改善集中於 worker daemon、lifecycle watcher／final status sync、result collector、Redis persistence、Alembic schema migration，以及 IaC／GitOps alignment。Multi-node GPU／RDMA performance 需另備硬體與驗證，現有 evidence 不涵蓋這些結論。
