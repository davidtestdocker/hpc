# Week6 — Kubernetes：從 Pod 到服務

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week5](../week5/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

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

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
