# HPC 系統軟體工程師／架構師版

## 專案標題

HPC／AI Kubernetes Workload Platform — GKE、Terraform、Kueue、JobSet

## 履歷摘要

以 FastAPI、Redis、PostgreSQL、Kubernetes JobSet 與 Kueue 建立 HPC workload
submission／scheduling／execution 平台，並將既有 GKE 納入 Terraform、驗證
隔離環境 lifecycle、網路政策與故障恢復。

## 建議 Bullet

- 以獨立 worker 自動提交與輪詢 MPI JobSet；驗證 worker 停止期間的新工作、
  submitted 工作在重啟後自動回收 ranks 0／1／2，且相同 job 僅有一個 JobSet；
  另驗證三次模擬 dispatch 失敗進入 failed／dead-letter，API 與 DB 狀態一致。

- 建立 `hpc-gpu-sg` 獨立 Terraform root module，將既有 zonal GKE、CPU
  system pool 與 L4 GPU pool import 後收斂至 zero drift；另完成隔離 cluster
  `3 add → RUNNING → zero drift → 3 destroy` lifecycle rehearsal。
- 實作釘版 JobSet／Kueue controller、queue、runtime Secrets 與 platform overlay
  的新叢集 bootstrap；以 SHA-256 驗證來源並加入區域／全域 GPU quota preflight，
  在全新 CPU-only GKE 完成 apply、rollout、health／RBAC 驗收與 destroy；另實測
  GPU quota 阻擋後由獨立 Terraform state 清理 3 個資源。
- 整合 FastAPI／Redis／PostgreSQL 與 Kubernetes Python Client，透過 Kueue
  admission 動態提交 JobSet；實測一筆 API job 由 accepted／submitted 收斂至
  completed，回收 MPI ranks 0／1／2並同步 PostgreSQL status。
- 排查 system-pool request 容量造成的 JobSet controller Pending，調整 demo
  request 後恢復 controller；將空 Redis 遷移至 PVC，驗證 Pod replacement 後
  test key 保留與 API 恢復。
- 在 Terraform 建立的 Calico rehearsal GKE 驗證 NetworkPolicy：policy 前兩個
  clients 可通，套用後 labeled client 可通、unlabeled client timeout，移除後
  連線恢復；完成後 destroy 並確認 state 空白／GKE 404。
- 實作最小權限 collector RBAC，只允許 list Pods／get logs，驗證 delete Pods
  維持拒絕；整理 Kueue TAS／priority、JobSet recovery、Ray retry、Slurm
  multi-node MPI 與 NCCL transport fallback 的跨層排障案例。

## 面試邊界

2026-09-22 已完成 polling worker／collector 與 restart acceptance；仍缺 GCS remote state、完整 GitOps、
全新 GPU cluster 的 MPI 驗收、artifact storage 與跨 Redis／PostgreSQL 原子交易。NetworkPolicy
封包驗證在隔離 Calico cluster，主 cluster enforcement 仍關閉。
