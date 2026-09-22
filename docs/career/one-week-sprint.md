# 一週作品衝刺

起始日期：2026-09-21。以現有工具完成可重建、可管理、可量測的主線。
日期是安排目標，以下逐項列出實際交付與驗證範圍；完成核心展示不等同 production-ready。
2026-09-22 已完成 Day 4 自動 worker 實機驗收，並補上 Day 5／6 的 13M causal LM
baseline、交錯 batch 比較與真實 CUDA traces。Day 7 展示入口及最新驗收見
[本輪 demo](../demo/interview-demo-20260922.md)。本輪採小型語言模型與單 L4 範圍，
不代表兩份職缺所有條件或完整 production 能力都已涵蓋。

| 階段 | 交付與驗收 | 狀態 |
|---|---|---|
| Day 1 | 現況盤點、主環境設定獨立、部署檢查入口 | 主環境與部署入口已建立；初次盤點找到 controller Pending，修復後 preflight 通過，保留前後證據 |
| Day 2 | IaC 對齊、處理容量與 Redis 遷移、部署／重建驗收 | controller／Redis 修復、主平台重新部署、Terraform zero drift、全新 CPU-only controllers／平台 bootstrap 與銷毀均已驗收；全新 GPU 重建未驗證，不阻擋單 GPU 路線 |
| Day 3 | 網路允許／拒絕測試、一次恢復到成功的演練 | 隔離 Calico GKE 完成 baseline、allow、deny timeout、移除 policy 後恢復；controller／Redis 恢復已驗證；歷史 MPI 狀態恢復受 webhook 阻礙 |
| Day 4 | 真實 benchmark 的 worker、最終狀態與結果回收 | 已完成限定 MPI 範圍：9/22 自動 dispatch／collect、queued／submitted 重啟接續、模擬失敗、DB 狀態核對通過，見 [自動驗收](../evidence/automatic-worker-20260922.json)；MPI 為 rank smoke test |
| Day 5 | 小型 LLM 訓練 baseline、暖機、重複量測 | 限定小型 causal LM 範圍完成：13M、文字 byte tokens、BF16、20 warmup＋3×40 measured steps；causality check 通過，非 pretrained LLM |
| Day 6 | 調校實驗、profile、改善或無改善的原因分析 | 完成：8→16 byte-token throughput +81.29%、latency +10.25%、memory +41.96%；兩份獨立 CUDA traces 支持固定成本攤薄分析 |
| Day 7 | 整體 demo、證據索引與兩版履歷 | 已整理本輪 demo、README／架構／索引／履歷；驗收以 demo 連結的實機 JSON、trace、平台檢查為準 |

## 9/21 變更歷程

- 新增 [平台操作入口](../runbooks/platform-bootstrap.md) 與 `scripts/platform.py`。
- 主環境獨立 values，明確 system-pool placement，關閉未配置的 Ingress。
- Redis Deployment／PVC 已套用：來源全部 DB 為空，測試 key 在 Pod 替換後仍存在，API 已恢復；不宣稱已支援非空資料遷移。
- 主環境不再渲染內嵌資料庫密碼，沿用外部建立的 Secret。
- 保存 [唯讀 preflight](../evidence/platform-preflight-20260921.json)：結果為失敗，原因是 JobSet controller 不可用。
- controller request 調整後 Running，[修復後 preflight](../evidence/platform-preflight-after-20260921.json) 全部通過；僅代表前置條件，不等於 workload 成功。
- 新增遷移與 stale hostname placement 恢復工具，保護條件納入測試。
- [本輪完整紀錄](../demo/platform-recovery-20260921.md)：新 MPI JobSet Completed、三個 rank 成功；舊 MPI 狀態恢復失敗與 root cause 分開記錄。
- MPI 模板新增 launcher successPolicy 與 child Job deadline；新模板與 collector 已打包 rollout，API lifecycle 驗收成功。
- 新增 `terraform/environments/gpu-sg`；現有 cluster／兩個 pools 匯入後 plan 為零變更。隔離 CPU-only cluster 已完成 3-resource apply、RUNNING／zero-drift 驗收及 3-resource destroy；後續 controllers／平台 bootstrap 驗收見下一節。remote state 與 Argo CD 對齊仍待完成。
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
