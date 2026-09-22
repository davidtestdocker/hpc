# Week3 — Docker：把程式與執行环境分開

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week2](../week2/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
