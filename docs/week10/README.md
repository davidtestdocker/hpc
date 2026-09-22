# Week10 — CI 與測試：不同檢查證明不同事情

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week9](../week9/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

CI 自動執行語法、風格、測試和建置檢查；CD 才涉及發佈與部署。mock 用假的外部系統驗證程式分支，不能取代真實 Redis／DB／Kubernetes 驗收。

目前本機驗證入口是 PYTHONPATH=. .venv/bin/pytest -q tests，包含 53 項測試。既有 workflow 使用 python -m pytest 和 ruff check .，範圍與本機命令不同，不能聲稱這次本機通過代表遠端 CI 全部通過。

CI 會寫 values-dev.yaml，既有 Argo dev 讀 overlays/dev；主 overlay 使用獨立 api-values.yaml。此差異保留並明寫，文件現行化不會暗中修改會推送或部署的 pipeline。

## 目前環境與實測邊界

直接讀歷史測試結果與 CI 設定；本輪沒有重跑測試，不觸發 push、映像發佈或 Argo 同步。

[本週實作／證據入口](<../../tests/test_worker.py>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：CI／CD 基礎](<Day1-CICD-Foundation.md>)
- [Day2：GitHub Actions workflow](<Day2-First-GitHub-ActionsCI-Pipeline.md>)
- [Day3：Ruff 與程式品質](<Day3-CodeQuality-withRuff.md>)
- [Day4：pytest 與斷言](<Day4-Pytest-API-Testing-Foundation.md>)
- [Day5：Mock 與故障分支](<Day5-Pytest-MockCI-Integration.md>)
- [Day6：CI 建置映像](<Day6-Docker-Build-inCI.md>)
- [Day7：GitOps image tag 路徑](<Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
