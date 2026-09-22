# Week8 — Helm、Kustomize、GitOps 的責任分工

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week7](../week7/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Helm 用 values 套入模板，產生 Kubernetes YAML；Kustomize 將基礎資源加上環境差異。兩者在本專案透過 helmCharts 與 patches 組合，渲染本身不等於部署。

Argo CD 對照 Git 宣告與叢集狀態並同步。Application 的 source 決定讀哪條路徑，destination 決定寫去哪裡；prune 可刪除不再宣告的受管資源，selfHeal 可覆蓋人工修改。

現行主 overlay 是 gpu-sg-platform，既有 Argo dev 仍指 overlays/dev。不能為了教材看起來整齊就把它描述成同一條已驗證 GitOps pipeline，更不能未審 diff 就切路徑同步。

## 目前環境與實測邊界

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

[本週實作／證據入口](<../evidence/platform-deployment-20260921.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：GitOps 的期望狀態](<Day1_GitOps_Foundation.md>)
- [Day2：Helm 的 values 與模板](<Day2_Helm_Foundation.md>)
- [Day3：平台 Chart 拆分](<Day3_Helmize_Platform.md>)
- [Day4：Helm 條件與共用命名](<Day4_Helm_Advanced.md>)
- [Day5：Kustomize overlay](<Day5_Kustomize_Foundation.md>)
- [Day6：Helm 與 Kustomize 整合](<Day6-Helm-Kustomize-Integration.md>)
- [Day7：多環境與 Argo 邊界](<Day7-GitOps_Multi_Environment_Integration.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
