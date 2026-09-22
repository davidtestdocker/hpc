# 從基礎到現行專案：學習入口

現行教材版本：2026-09-22。從 Week1 開始，不必先看懂平台架構。Week1～20 的每日正文已改寫為現行教學；舊版全文獨立保存，不再要求讀者自行在舊操作和新流程之間拼湊。

## 固定閱讀順序

1. 先讀該週 README 的基礎解說，建立本週名詞與因果關係。
2. 按 Day 順序讀：概念 → 現行 source／設定片段 → 練習 → 判讀。Week13 Day7 子章依 7-1～7-7，最後讀報告；Week14 現存課程由 Day2 開始。
3. 每課自己回答「解決什麼、流程是什麼、如何驗證、限制在哪」，卡住就回前面的基礎，不直接背架構圖。
4. 選[本機與離線練習](current-environment.md)實作。需要部署／壓測／故障注入時才依 runbook，先確認目標與影響。
5. 完成相關基礎後，再讀[整體架構](architecture/platform-architecture.md)、[README](../README.md)和[面試導覽](interview/project-interview-guide.md)。

## 版本與證據

- 138 篇每日教材為現行版，另外新增 20 篇每週基礎／目錄。
- [完整舊版索引](history/20260922-before-current/README.md)保存改寫前原文，SHA-256 可核對。它包含舊命令、成功／失敗及環境紀錄，不拿來當今天的操作手冊。
- JSON／log／trace／執行時程式快照留在原路徑，沒有改成新環境數據。
- 現行版指對齊 repo 實作，不保證即時可用。Argo CD、Slurm、Ray 等未納入主線的部分仍教，但明確標為獨立設定／實驗，不捏造整合。
- 教材中的片段是閱讀起點，不是可獨立 apply 的 YAML 或完整可執行程式。完整檔案與操作入口均另附連結。

## 逐週入口

<a id="week1"></a>

### Week1：Linux：先理解服務如何執行

[先讀本週基礎與每日目錄](week1/README.md)。本週在自己的 Linux 學習環境做唯讀觀察，不聲稱主叢集當下健康。

<a id="week2"></a>

### Week2：Python：讀懂平台程式的最小基礎

[先讀本週基礎與每日目錄](week2/README.md)。本週先閱讀與執行純 Python 小例子；不要直接啟動依賴雲端的 worker。

<a id="week3"></a>

### Week3：Docker：把程式與執行环境分開

[先讀本週基礎與每日目錄](week3/README.md)。本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

<a id="week4"></a>

### Week4：API：提交工作不等於同步執行

[先讀本週基礎與每日目錄](week4/README.md)。現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

<a id="week5"></a>

### Week5：持久化與可恢復 worker

[先讀本週基礎與每日目錄](week5/README.md)。主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

<a id="week6"></a>

### Week6：Kubernetes：從 Pod 到服務

[先讀本週基礎與每日目錄](week6/README.md)。K3s 是獨立基礎練習選項，不是本次主環境；雲端修改只依 runbook。

<a id="week7"></a>

### Week7：Kubernetes：設定、資源與對外入口

[先讀本週基礎與每日目錄](week7/README.md)。學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

<a id="week8"></a>

### Week8：Helm、Kustomize、GitOps 的責任分工

[先讀本週基礎與每日目錄](week8/README.md)。主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

<a id="week9"></a>

### Week9：Terraform：資源身分與建置生命週期

[先讀本週基礎與每日目錄](week9/README.md)。本週只讀設定與既有證據；雲端 apply／destroy 須依 runbook 明確確認目標，GPU quota 固定一張。

<a id="week10"></a>

### Week10：CI 與測試：不同檢查證明不同事情

[先讀本週基礎與每日目錄](week10/README.md)。只跑本機測試／離線讀 CI；不觸發 push、映像發佈或 Argo 同步。

<a id="week11"></a>

### Week11：Observability：指標的來源與意義

[先讀本週基礎與每日目錄](week11/README.md)。監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

<a id="week12"></a>

### Week12：Linux 效能工具：以假說選工具

[先讀本週基礎與每日目錄](week12/README.md)。歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

<a id="week13"></a>

### Week13：Benchmark：從負載定義到可重算結果

[先讀本週基礎與每日目錄](week13/README.md)。Day7 的子章按 7-1 到 7-7 閱讀，最後讀 day7-benchmark-report；不新增負載或覆寫舊結果。

<a id="week14"></a>

### Week14：GPU：硬體、runtime 與排程分層

[先讀本週基礎與每日目錄](week14/README.md)。現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

<a id="week15"></a>

### Week15：模型 runtime 與現行單卡訓練

[先讀本週基礎與每日目錄](week15/README.md)。單 L4／小模型可重現實驗；無 pretrained 品質、多 GPU 或 RDMA 結論。

<a id="week16"></a>

### Week16：分散式訓練：process、device 與通訊

[先讀本週基礎與每日目錄](week16/README.md)。現有 CPU／Gloo、單 rank NCCL 與單 GPU 訓練分開保存；未驗證多 GPU scaling。

<a id="week17"></a>

### Week17：MPI、Slurm、Ray：分散式工作不同層

[先讀本週基礎與每日目錄](week17/README.md)。Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

<a id="week18"></a>

### Week18：網路排障：由近到遠建立證據

[先讀本週基礎與每日目錄](week18/README.md)。本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

<a id="week19"></a>

### Week19：准入與工作群組：Kueue／JobSet

[先讀本週基礎與每日目錄](week19/README.md)。單實體 L4，CPU MPI rank smoke；Kueue quota 與 time-sharing share 都不是實體卡數。

<a id="week20"></a>

### Week20：安全、恢復與架構取捨

[先讀本週基礎與每日目錄](week20/README.md)。保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

## 註解與操作教材的分工

Argo CD、Terraform、Helm／Kustomize／Kubernetes YAML 與新版 Python 主線已有中文註解；不宣稱所有歷史或第三方檔案都逐行註解。每日教材解釋設計與使用情境，檔案註解說明欄位與控制流程，runbook 管實際操作與驗收。

主部署鏈為 Terraform → bootstrap → Helm／Kustomize → deploy／rollout → 驗收；既有 Argo dev 仍指舊 overlay。學 Argo CD 不需要擅自切換 Application path 或執行 prune。

最先開始：[Week1 基礎](week1/README.md) → [Day1 程序與 PID](week1/day1-linux-process.md)。
