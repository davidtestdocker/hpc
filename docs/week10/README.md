# Week10 — CI 與測試：不同檢查證明不同事情

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week9](../week9/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

CI 自動執行語法、風格、測試和建置檢查；CD 才涉及發佈與部署。mock 用假的外部系統驗證程式分支，不能取代真實 Redis／DB／Kubernetes 驗收。

目前本機驗證入口是 PYTHONPATH=. .venv/bin/pytest -q tests，包含 53 項測試。既有 workflow 使用 python -m pytest 和 ruff check .，範圍與本機命令不同，不能聲稱這次本機通過代表遠端 CI 全部通過。

CI 會寫 values-dev.yaml，既有 Argo dev 讀 overlays/dev；主 overlay 使用獨立 api-values.yaml。此差異保留並明寫，文件現行化不會暗中修改會推送或部署的 pipeline。

## 目前環境與實測邊界

只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

[本週實作／證據入口](<../../tests/test_worker.py>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：CI／CD 基礎](<Day1-CICD-Foundation.md>)
- [Day2：GitHub Actions workflow](<Day2-First-GitHub-ActionsCI-Pipeline.md>)
- [Day3：Ruff 與程式品質](<Day3-CodeQuality-withRuff.md>)
- [Day4：pytest 與斷言](<Day4-Pytest-API-Testing-Foundation.md>)
- [Day5：Mock 與故障分支](<Day5-Pytest-MockCI-Integration.md>)
- [Day6：CI 建置映像](<Day6-Docker-Build-inCI.md>)
- [Day7：GitOps image tag 路徑](<Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
