# Week20 — 安全、恢復與架構取捨

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week19](../week19/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

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

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
