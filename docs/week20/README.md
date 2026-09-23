# Week20 — 安全、恢復與架構取捨

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week19](../week19/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

ServiceAccount 是 Pod 呼叫 Kubernetes API 的身份，Role／Binding 決定可操作的資源與 verbs。Secret 保存敏感值但不是把明文提交 Git 的理由；NetworkPolicy 是另一層封包控制。

恢復要先定義 failure domain：程序、Pod、node、資料或跨服務一致性。worker 重啟、Redis Pod 替換、JobSet 整組 Recreate 是不同案例，不可合併成全面 HA。

最後用工作負载需求解釋選型：誰接單、誰准入、誰排程、誰儲存、誰收結果。工具越多不是越完整；已驗證範圍、可操作步驟與已知失敗邊界才是面試與維護的重點。

## 目前環境與實測邊界

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

## 本週材料怎麼讀

- **Day1～Day2：身份、權限與 Pod 安全** — [Role](../../k8s/security/role.yaml)、[RoleBinding](../../k8s/security/rolebinding.yaml) 與 [測試 Pod](../../k8s/security/rbac-api-test.yaml) 對照讀取權限與 securityContext；[api-jobset-rbac.yaml](../../k8s/security/api-jobset-rbac.yaml) 是主 worker 的另一組權限。
- **Day3：封包隔離** — [allow-client-to-server.yaml](../../k8s/security/network-policy/allow-client-to-server.yaml) 對照來源標籤與目的埠，再看 [隔離 Calico 叢集的驗收 JSON](../evidence/network-policy-validation-20260921.json) 中 allow、deny、移除後恢復的結果。
- **Day4：重建與恢復** — [JobSet 範例](../../k8s/gpu-scheduling/examples/jobset-mpi.yaml) 和 [node failure 測試設定](../../k8s/recovery/gpu-node-failure-test.yaml) 搭配課文的重建、cordon 紀錄閱讀；JobsReady 與原運算成功是不同結果。
- **Day5：跨層排障** — [Ray 資源不符案例](../../ray-resource-mismatch-job.yaml)、[Ray 重試案例](../../ray-worker-recovery-job.yaml)、[Slurm Pending 案例](../../slurm/pending-cpu-test.sbatch) 分別對應課文的資源等待與重試觀察。
- **Day6：選型說明** — 材料是正文的架構比較與取捨，沒有一支將所有列出工具串接起來的程式。

## 每日閱讀順序

- [Day1：RBAC 與最小權限](<day1-rbac-serviceaccount-least-privilege.md>)
- [Day2：Pod、image 與 Secret 安全](<day2-pod-image-secret-security.md>)
- [Day3：NetworkPolicy 與隔離](<day3-networkpolicy-tenant-isolation.md>)
- [Day4：恢復與 HA 邊界](<day4-ha-node-failure-recovery.md>)
- [Day5：跨層 production troubleshooting](<day5-ai-hpc-production-troubleshooting.md>)
- [Day6：架構選型與整體說明](<day6-ai-hpc-platform-technology-selection.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
