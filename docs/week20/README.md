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

[本週實作／證據入口](<../evidence/automatic-worker-20260922.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

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
