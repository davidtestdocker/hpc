# Week6 — Kubernetes：從 Pod 到服務

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week5](../week5/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

Kubernetes 透過 API 保存期望狀態，controller 持續協調，Scheduler 決定 Pod 放到哪個 node。Pod 是共同網路與生命週期的基本單位，不等於 VM。

Deployment 管理可替換的服務 Pod；Service 用 selector 連到符合 labels 的端點。DNS 名稱不是固定 Pod IP。資料需用合適的持久化設計，不能假設重建的 Pod 還有原本的可寫層。

主平台使用 GKE hpc-gpu-sg 與 namespace hpc-platform-dev。API／worker／Redis／PostgreSQL 放在 system-pool；MPI 可以共置於 GPU node 但工作本身請求 CPU。學習 Kubernetes 不需要先把 GKE 拆掉重建。

## 目前環境與實測邊界

### 先讀懂 YAML 的形狀

以下只是語法示意，不是要套用的完整資源：

```yaml
metadata:
  name: example
  labels:
    app: example
spec:
  containers:
    - name: app
      image: example:tag
```

`key: value` 是鍵值，縮排表示從屬關係，`-` 表示清單項目。上例 metadata 和 spec 同層；labels 屬 metadata，containers 屬 spec。不同 kind 的 spec 結構不同：Deployment 把 Pod 設定放在 spec.template.spec，不能將這份示意直接貼到任何位置。

實際資源先讀 apiVersion／kind／metadata，再追 spec。`metadata.labels` 和 selector 對不齊時，物件各自存在也不代表彼此有連上。

K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

[本週實作／證據入口](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Kubernetes 控制迴圈](<Day1_Kubernetes_Foundation.md>)
- [Day2：Pod 的範圍](<Day2_Pod_Foundation.md>)
- [Day3：Deployment 與副本](<Day3_Deployment_Foundation.md>)
- [Day4：Service 與 selector](<Day4_Service_Foundation.md>)
- [Day5：K3s 與 GKE 邊界](<Day5_K3s_Foundation.md>)
- [Day6：API 與 Redis 部署依賴](<Day6_Deploy_API_and_Redis.md>)
- [Day7：完整平台驗收](<Day7_Complete_Platform_on_Kubernetes.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
