# Week8 — Helm、Kustomize、GitOps 的責任分工

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week7](../week7/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

Helm 用 values 套入模板，產生 Kubernetes YAML；Kustomize 將基礎資源加上環境差異。兩者在本專案透過 helmCharts 與 patches 組合，渲染本身不等於部署。

Argo CD 對照 Git 宣告與叢集狀態並同步。Application 的 source 決定讀哪條路徑，destination 決定寫去哪裡；prune 可刪除不再宣告的受管資源，selfHeal 可覆蓋人工修改。

現行主 overlay 是 gpu-sg-platform，既有 Argo dev 仍指 overlays/dev。不能為了教材看起來整齊就把它描述成同一條已驗證 GitOps pipeline，更不能未審 diff 就切路徑同步。

## 目前環境與實測邊界

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

## 本週材料怎麼讀

- **Day1、Day7：GitOps 讀哪裡、部署到哪裡** — [Argo Application](../../argocd/application-dev.yaml) 看 `source`、`destination`、同步設定；[AppProject](../../argocd/project.yaml) 看允許範圍。
- **Day2～Day4：Helm 如何產生 YAML** — 對照 [values.yaml](../../helm/api/values.yaml)、[Deployment 模板](../../helm/api/templates/deployment.yaml) 和 [命名 helper](../../helm/api/templates/_helpers.tpl)，追一個 value 如何被模板使用。
- **Day5～Day6：環境差異如何組合** — [dev kustomization](../../kustomize/overlays/dev/kustomization.yaml) 看 `helmCharts` 與 patches；再對照 [主平台 kustomization](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。兩份設定的用途不同，Argo dev 指向前者。
- **保存結果** — 各課正文保留渲染、部署與錯誤觀察；讀到 `Expected` 時將它視為預期示例，不能當成實際輸出。

## 每日閱讀順序

- [Day1：GitOps 的期望狀態](<Day1_GitOps_Foundation.md>)
- [Day2：Helm 的 values 與模板](<Day2_Helm_Foundation.md>)
- [Day3：平台 Chart 拆分](<Day3_Helmize_Platform.md>)
- [Day4：Helm 條件與共用命名](<Day4_Helm_Advanced.md>)
- [Day5：Kustomize overlay](<Day5_Kustomize_Foundation.md>)
- [Day6：Helm 與 Kustomize 整合](<Day6-Helm-Kustomize-Integration.md>)
- [Day7：多環境與 Argo 邊界](<Day7-GitOps_Multi_Environment_Integration.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
