# Week17 — MPI、Slurm、Ray：分散式工作不同層

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week16](../week16/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

MPI 是程序間通訊模型，rank 識別參與者；launcher 啟動程序，worker 執行程式。rank/hostname 輸出證明啟動與連線，不是 bandwidth benchmark。

Slurm 分配叢集資源並執行 batch job，Ray 排程 task／actor，Kubernetes 排程 Pod；多層並存時各有資源視圖。Kueue 准入則在工作啟動前處理 quota，不取代這些 scheduler。

主 API 使用 JobSet 管理 CPU MPI；歷史 Slurm CPU VM 和 Ray 案例獨立。主平台三個 workers 可共置一台 node，不能把三個 Pod 寫成三台實體機。

## 目前環境與實測邊界

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

## 本週材料怎麼讀

- **Day1：MPI 程序與通訊** — 從 [mpi_hello.c](../../mpi_hello.c) 的 rank 輸出開始，再看 [send/recv](../../mpi_send_recv.c)、[broadcast](../../mpi_broadcast.c)、[reduce](../../mpi_reduce.c)、[allreduce](../../mpi_allreduce.c) 的呼叫。
- **Day2～Day3：效能工具與通訊堆疊** — OSU benchmark、RDMA 裝置查詢的命令與當時結果在課文；OSU 工具原始碼未保存於本專案。
- **Day4：Slurm 跨節點啟動** — [mpi-multinode.slurm](../../mpi-multinode.slurm) 看資源申請與 MPI 啟動命令，搭配課文的 allocation／hostname 紀錄理解程序放在哪裡。
- **Day5～Day6：Ray 與排程層** — [ray-cluster.yaml](../../ray-cluster.yaml) 定義 head／worker，[ray-job.yaml](../../ray-job.yaml) 定義示範 task。課文的 Actor 範例與資源不足觀察另在正文；自動 MPI worker 驗收無法代替這些 Slurm／Ray 案例。

## 每日閱讀順序

- [Day1：MPI rank 與 launcher](<day1-mpi-fundamentals.md>)
- [Day2：MPI 效能測試](<day2-mpi-performance-benchmark.md>)
- [Day3：HPC communication stack](<day3-hpc-communication-stack.md>)
- [Day4：Slurm 多節點 CPU 案例](<day4-slurm-multinode-hpc-cluster.md>)
- [Day5：Ray 與 KubeRay](<day5-ray-kuberay-distributed-computing.md>)
- [Day6：排程層整合](<day6-cluster-scheduling-integration.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
