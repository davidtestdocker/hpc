# Week3 — Docker：把程式與執行环境分開

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week2](../week2/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Image 是分層的檔案系統與啟動設定；container 是用該 image 啟動的程序環境。容器共享 host kernel，不是完整 VM，也不自動帶有 Kubernetes 控制器。

Dockerfile 描述建置步驟；build context 決定可 COPY 的範圍。映像標籤可以改指向，digest 用來固定內容。環境變數和 volume 是執行時設定，不應把真實秘密烘進 image。

Compose 管理本機多服務；service 名稱只在相應網路中解析。主平台使用 GKE；本機設定需要另核對連線與初始化，不能把 compose up 當成整個 HPC 平台驗收。

## 目前環境與實測邊界

本週以檢查與離線讀設定為主；不要求安裝另一個 Docker daemon 或啟動正式服務。

[本週實作／證據入口](<../../docker/Dockerfile>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：為何容器化](<day1-why-docker.md>)
- [Day2：確認 Docker 執行環境](<day2-install-docker.md>)
- [Day3：Image 與 container](<day3-image-container.md>)
- [Day4：Dockerfile 與 build context](<day4-dockerfile.md>)
- [Day5：Compose 與服務連線](<day5-docker-compose.md>)
- [Day6：監控程式容器化](<day6-containerize-monitoring.md>)
- [Day7：Docker 到平台部署](<day7-docker-integration.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
