# 教材核對結案與重要限制

核對日期：2026-09-22；來源為此儲存庫現有程式、設定、138 篇課文及保存證據。本輪未連雲端、啟動 VM、執行 workload 或重新量測效能。

## 怎麼讀

從 [Week1](../week1/README.md) 開始，依每週目錄順序：基礎解說 → 每課頁首修正 → 已有結果與解讀 → 原始完整教材。頁首與原文不一致時，以頁首對現行版本的說明為準；原文保留當時成功、失敗和做法，不是假裝全部仍適用。

138 篇的證據來源、摘錄、修正與程式 hashes 見[稽核清單](curriculum-content-audit.md)。原始教材仍是 `.md`；主教材原始正文與 44 份受保護 JSON／log／trace 等證據均以 SHA-256 核對，不補造缺少的歷史輸出。概念課没有實測時直接說明，不要求讀者補跑。

## 本輪發現、已寫入教材但未修改實作的問題

| 範圍 | 現存限制 | 閱讀時的正確結論 |
|---|---|---|
| [pgbench runner](../../benchmark/postgres/run_pgbench.sh) | `pgbench \| tee` 未啟用 pipefail，可能掩蓋測試失敗 | 外層 PASS 不是有效量測的充分證據；Week13 已標註 |
| [舊 GPU runtime overlay](../../kustomize/overlays/gpu-sg/kustomization.yaml) | 平面 ConfigMap 未提供現行 runtime 所需完整 Python 套件結構 | 不保證舊直接執行入口仍能使用；與獨立 causal LM runner 分開 |
| [效能 analyzer](../../analysis/performance_analyzer.py) | 只讀三份 vLLM JSON、用百分比規則標示趨勢 | 沒有自動讀 training profiler、診斷硬體或匯入 Prometheus |
| [CPU scaling](../../runtime/pytorch/distributed_scaling.py) | 未固定共用資料 seed、未取最慢 rank 時間、計入 profiler；比較的 CPU 限額及 global batch 不同 | 0.955x 是歷史觀察，不能歸因單一通訊瓶頸 |
| [RBAC 測試 Pod](../../k8s/security/rbac-api-test.yaml) | 列印 HTTP code，但沒有 assert 預期值 | Completed 不代表 allow／deny 驗收全對，要讀保存的 HTTP 結果 |
| [Compose](../../compose.yaml) | 本機配置與主 overlay 的服務／worker 路徑不同 | 不能把 Compose 當現行 GKE 平台一鍵完整重建入口 |

這些限制已揭露，不等於本輪已修好或重新驗證；避免為了文件「全綠」而擴張成部署或程式改造。

## 不能合併成同一份成功證據

- 主線：CPU MPI 三個 rank／worker Pods；不代表三台 node，不是多 GPU 或通信頻寬測試。
- 訓練：13M causal LM、單 L4 的獨立 runner；未接 MPI API，不是大型預訓練模型品質或多 GPU scaling 驗收。
- Week15 舊 vLLM sweep 的 request 數不全相同；Day6 的固定 128 prompts 比較也缺重複量測，不能把最高數字當通用容量。
- Week19 TAS：當時兩個 Pod 指派到同 node，但仍 ContainerCreating；只有 placement 證據，未取得執行成功或拓樸效能改善。
- 網路：隔離 Calico 叢集測過 ingress allow／deny／恢復；主環境 enforcement 仍關，未驗證完整 DNS／egress／跨租戶 policy 組合。
- 恢復：worker 重啟接續、Redis Pod 替換與舊 JobSet 重建是不同案例；JobsReady 不等於原工作 Completed，也不等於 node failover、checkpoint 續跑或 Redis 全失恢復。
- 安全：測試 Pod 的 digest／securityContext 不代表所有 charts 都完成同樣 hardening；本輪沒有漏洞掃描或秘密輪替證據。
- OpenStack、HTCondor、LSF、DLRover 是選型教材，沒有實作結果；Slurm／Ray 是獨立歷史實驗，不是主 API 支援的 backend。

## 離線檢查的意義

[本輪實際檢查結果](curriculum-validation-20260922.json)：138 篇、20 個每週入口、188 個頁面、1,964 個本地連結，44 份受保護證據 hashes；錯誤 0。原文完整性、摘錄來源及所核對程式 hashes 檢查通過，diff whitespace 檢查通過。

`python3 scripts/check_curriculum.py` 只檢查本地連結、教材結構、原文／證據 hashes、稽核清單及所核對程式版本；不連叢集、不執行教材命令。內容正確性由逐篇核對處理，不把靜態檢查通過當成即時服務正常。

本輪文件交付已完成；未保存的歷史 raw log 不能事後補造。付費資源是否已刪除不在本輪操作範圍，不能用文件完成推論雲端已停止計費。
