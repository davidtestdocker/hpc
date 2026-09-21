# 一週作品衝刺

起始日期：2026-09-21。以現有工具完成可重建、可管理、可量測的主線。
日期是安排目標，完成狀態以實測證據為準；七個階段的本輪交付已完成，
尚未涵蓋的 production 邊界列在各項說明與 Evidence Index。

| 階段 | 交付與驗收 | 狀態 |
|---|---|---|
| Day 1 | 現況盤點、主環境設定獨立、部署檢查入口 | 已有程式與離線驗證；唯讀盤點找到 JobSet Pending |
| Day 2 | IaC 對齊、處理容量與 Redis 遷移、部署／重建驗收 | controller、Redis 驗收成功；Terraform import 零 drift，隔離 cluster 完成 lifecycle；釘版 bootstrap 實作與 server dry-run 通過，全新 GPU cluster 執行待驗證 |
| Day 3 | 網路允許／拒絕測試、一次恢復到成功的演練 | 隔離 Calico GKE 完成 baseline、allow、deny timeout、移除 policy 後恢復；controller／Redis 恢復已驗證；歷史 MPI 狀態恢復受 webhook 阻礙 |
| Day 4 | 真實 benchmark 的 worker、最終狀態與結果回收 | MPI completion collector 已部署；API job 實測 accepted → submitted → completed，ranks 與 PostgreSQL status 回寫成功；兩個 worker endpoint 仍需手動觸發 |
| Day 5 | 小型 LLM 訓練 baseline、暖機、重複量測 | L4 synthetic Transformer BF16：10 warmup、3×20 measured steps，raw JSON 已保存 |
| Day 6 | 調校實驗、profile、改善或無改善的原因分析 | batch 8→16 單變因：tokens/s +74.4%、step latency +14.0%、peak memory +50.8%，限制已記錄 |
| Day 7 | 整體 demo、證據索引與兩版履歷 | Evidence index／runbook 已更新；完成 HPC 系統架構版與 AI 效能版履歷 bullets |

## 本輪變更

- 新增 [平台操作入口](../runbooks/platform-bootstrap.md) 與 `scripts/platform.py`。
- 主環境獨立 values，明確 system-pool placement，關閉未配置的 Ingress。
- Redis Deployment／PVC 已套用：來源全部 DB 為空，測試 key 在 Pod 替換後仍存在，API 已恢復；不宣稱已支援非空資料遷移。
- 主環境不再渲染內嵌資料庫密碼，沿用外部建立的 Secret。
- 保存 [唯讀 preflight](../evidence/platform-preflight-20260921.json)：結果為失敗，原因是 JobSet controller 不可用。
- controller request 調整後 Running，[修復後 preflight](../evidence/platform-preflight-after-20260921.json) 全部通過；僅代表前置條件，不等於 workload 成功。
- 新增遷移與 stale hostname placement 恢復工具，保護條件納入測試。
- [本輪完整紀錄](../demo/platform-recovery-20260921.md)：新 MPI JobSet Completed、三個 rank 成功；舊 MPI 狀態恢復失敗與 root cause 分開記錄。
- MPI 模板新增 launcher successPolicy 與 child Job deadline；新模板與 collector 已打包 rollout，API lifecycle 驗收成功。
- 新增 `terraform/environments/gpu-sg`；現有 cluster／兩個 pools 匯入後 plan 為零變更。隔離 CPU-only cluster 已完成 3-resource apply、RUNNING／zero-drift 驗收及 3-resource destroy。remote state、Kubernetes bootstrap 與 Argo CD 對齊仍待完成，不能宣稱完整平台已從零重建。
- Terraform rehearsal 啟用 Calico 後完成 NetworkPolicy packet test：policy 前兩個 clients 都成功；套用後 allowed 成功、denied timeout；移除 policy 後 denied 恢復。測試 cluster 已 destroy，主 cluster enforcement 維持關閉。
- 新增並部署 MPI completion collector；最小 RBAC 允許 list Pods／get logs 但拒絕 delete Pods。[API lifecycle evidence](../evidence/mpi-api-lifecycle-20260921.json) 保存真實 JobSet Completed、ranks 0／1／2、Redis/API 與 PostgreSQL completed。
- 完成 [HPC 系統架構版](resume-hpc-system.md) 與 [AI 效能版](resume-ai-performance.md) 履歷 bullets；兩版共用 evidence，但排序與限制依職缺不同。

## 後續補強：平台部署入口

新增 `scripts/deploy_platform.py`，預設只做前置檢查、Redis storage guard 與
server dry-run；`--execute` 才會部署並等待 rollout、初始化 DB。
已在主 GKE 完成 [dry-run 驗收](../evidence/platform-deploy-dry-run-20260921.json)，
後續已使用此工具套用完整 overlay，三個服務 rollout 與 DB 初始化通過；
API Service／Redis 連線及既有 MPI 工作在 Redis／PostgreSQL 的 completed 狀態
均驗收成功。後續又完成釘版 controllers、queues、Secrets 與平台部署的 bootstrap
工具及主叢集 server dry-run；空白 GPU 叢集的實際執行仍未完成。
另以 Spot L4 嘗試全新叢集；專案全域 GPU quota 1／1 阻擋 GPU pool，已保存
root cause、完成 3-resource destroy，並新增 apply 前 quota preflight。
改以零 GPU node 的全新 GKE 完成 controllers、queues、Secrets、完整平台部署、
health／RBAC／PVC／zero-diff 驗收及 3-resource destroy；GPU／MPI 範圍仍明確排除。

## 文件維護方式

Week 文件保留原始環境、log 與數據，在頂部連結現行入口。
現行架構與操作方式放入 architecture／runbooks；新結果放入 evidence。
設定完成、離線驗證、實際部署與 workload 成功分別標示，不互相替代。
