# Week7 — Kubernetes：設定、資源與對外入口

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week6](../week6/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

ConfigMap 放非秘密設定，Secret 放敏感設定但不因此自動成為安全的 Git 檔案。envFrom 將鍵值注入程序；修改設定後程序是否重新載入，取決於使用方式。

requests 供排程器計算容量；limits 限制執行時資源。readiness 決定能否接收 Service 流量，liveness 可觸發重啟。錯誤探針可能把外部依賴故障放大成重啟風暴。

ClusterIP、NodePort、Ingress 是不同流量入口。HPA 依指標調整指定 workload 副本，與 Kueue 准入或 node 自動擴容不是同一件事。

## 目前環境與實測邊界

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

## 本週材料怎麼讀

- **Day1～Day2：設定如何進入程序** — 對照 [ConfigMap](../../k8s/api-configmap.yaml)、[Secret 範例](../../k8s/postgres-secret.example.yaml) 與 [API Deployment](../../k8s/api-deployment.yaml) 的引用，追環境變數從哪裡來。
- **Day3～Day4：資源與探針** — 同一份 [API Deployment](../../k8s/api-deployment.yaml) 的 `resources`、`livenessProbe`、`readinessProbe` 對應本課欄位；探針查詢的路由實作在 [api/main.py](../../api/main.py)。
- **Day5～Day6：對外入口** — [Service](../../k8s/api-service.yaml) 的 NodePort 與 [Ingress](../../k8s/api-ingress.yaml) 的 host／path 是舊課程設定。課文保存當時連線結果；目前主 overlay 使用 ClusterIP 且停用 Ingress。
- **Day7：自動調整副本** — [api-hpa.yaml](../../k8s/api-hpa.yaml) 看目標 Deployment、CPU 指標與副本上下限；[loadtest/benchmark.js](../../loadtest/benchmark.js) 看當時送出的請求。HPA 調整的是 API 副本。

## 每日閱讀順序

- [Day1：ConfigMap 與環境變數](<Day1_ConfigMap.md>)
- [Day2：Secret 與身份](<Day2_Secret.md>)
- [Day3：Requests、limits 與 QoS](<Day3_Resource_Requests_Limits_QoS.md>)
- [Day4：Liveness 與 readiness](<Day4_Liveness_and_Readiness_Probe.md>)
- [Day5：Service type 與 NodePort](<Day5_Service_Types_NodePort.md>)
- [Day6：Ingress 與 Controller](<Day6_Ingress_Traefik.md>)
- [Day7：HPA 的作用範圍](<Day7_Horizontal_Pod_Autoscaler.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
