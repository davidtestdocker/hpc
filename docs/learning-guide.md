# 從基礎到現行專案：學習入口

閱讀版更新：2026-09-22。從 Week1 開始，直接看概念、已有結果與解讀；**不用再開 VM，也不要求你做本機測試**。

## 固定閱讀順序

1. 讀該週 README 的基礎解說。
2. 讀每日頁首的現行補充與「已有結果與解讀」。數據已直接列出，不需要你去跑出答案。
3. 往下讀「原始完整教材與當時輸出」：原本的詳細說明、程式與輸出已放回同一份 `.md`，沒有縮短取代。
4. 想一次看成果，可讀[已有結果總覽](current-environment.md)。基礎熟悉後再讀整體架構與 README。

Week13 Day7 子章依 7-1～7-7，最後讀報告；Week14 現存課程從 Day2 開始。原文的命令當作理解當時操作的材料，不是現在還要你再執行。

## 原文、格式與證據

- 138 篇原始完整正文已恢復到各自 `docs/week*/...md` 內；前面保留現行補充與相關的已保存結果。
- [原版 Markdown 索引](history/20260922-before-current/README.md)也恢復 `.md`，不是 `.txt`。副本只調整搬移後的相對連結；主教材下半部的原文可核對原始 SHA-256。
- 原始 JSON／log／trace／執行時程式快照沒有更動。
- 不是每課都存在新的實測。概念示例不冒充實機成功；沒有保存的結果不補造，歷史失敗也不改成成功。
- VM 是否仍在運行，不影響閱讀已保存內容；目前付費資源是否已停用則需另查，這次沒有進行雲端操作。

## 逐週入口

<a id="week1"></a>

### Week1：Linux：先理解服務如何執行

[先讀本週基礎與每日目錄](week1/README.md)。直接讀原本 Linux 指令輸出與概念解說，不需再執行。

<a id="week2"></a>

### Week2：Python：讀懂平台程式的最小基礎

[先讀本週基礎與每日目錄](week2/README.md)。直接讀原本 Python 程式與輸出，不需啟動 worker 或本機測試。

<a id="week3"></a>

### Week3：Docker：把程式與執行环境分開

[先讀本週基礎與每日目錄](week3/README.md)。只需閱讀設定解說與原有輸出，不用安裝或啟動服務。

<a id="week4"></a>

### Week4：API：提交工作不等於同步執行

[先讀本週基礎與每日目錄](week4/README.md)。現行 GKE 主線；本機讀已保存的驗收結果，不需要雲端權限。

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

[先讀本週基礎與每日目錄](week10/README.md)。直接讀已保存的測試結果與 CI 設定，不需重跑。

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

[先讀本週基礎與每日目錄](week18/README.md)。本週直接讀既有主機網路與封包觀察；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

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
