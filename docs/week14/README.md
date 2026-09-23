# Week14 — GPU：硬體、runtime 與排程分層

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week13](../week13/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

Driver 讓作業系統與 GPU 溝通；CUDA runtime 與框架執行運算；device plugin 讓 Kubernetes 宣告 GPU 資源。這些層任何一個缺失，都可能造成「看得到資源卻跑不了運算」。

主環境一張 NVIDIA L4，time-sharing 公布多個 share，沒有把硬體變成多張卡。request 一個 share 也不等於獨占，其他工作可能影響延遲與記憶體。

GPU utilization、VRAM used、PyTorch allocated／reserved、tokens/s 不是同一指標。歷史 P100 dashboard 與新 L4 實驗必須標不同來源。

## 目前環境與實測邊界

現存 Week14 從 Day2 開始，維持原檔案命名；不捏造不存在的 Day1 實驗。

## 本週材料怎麼讀

- **Day2、Day4：GPU 資源與 node pool** — 讀課文的節點資源、Pod 排程、`nvidia-smi` 輸出。舊 `gpu-test-pod.yaml` 沒有保存為獨立檔案。
- **Day3：指標路徑** — [Prometheus ConfigMap](../../helm/prometheus/templates/configmap.yaml) 用來對照 scrape 設定，配合課文理解 exporter → Prometheus → Grafana 的資料流。
- **Day5：DCGM 元件** — [nvidia-dcgm.yaml](../../benchmark/k8s/nvidia-dcgm.yaml) 和 [dcgm-exporter-remote.yaml](../../benchmark/k8s/dcgm-exporter-remote.yaml) 分別對照 hostengine 與 exporter 的部署、連線設定。
- **Day6：Dashboard 觀察** — 讀課文保存的 GPU 負載與指標觀察；`gpu_stress.cu` 未保存在儲存庫。後來的 L4 語言模型訓練報告不是這次 dashboard 實驗的輸出。

## 每日閱讀順序

- [Day2：GPU scheduling](<day2-kubernetes-gpu-scheduling.md>)
- [Day3：GPU 監控架構](<day3-gpu-monitoring-architecture.md>)
- [Day4：GKE GPU pool](<Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md>)
- [Day5：DCGM 指標整合](<Day5-GPU-Metrics-Monitoring-integration.md>)
- [Day6：Dashboard 與實驗驗證](<Day6-gpu-dashboard-establish-and-gpuworkload-verification.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
