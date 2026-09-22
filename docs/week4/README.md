# Week4 — API：提交工作不等於同步執行

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week3](../week3/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

HTTP method 與 path 共同識別介面。POST 可建立工作，GET 查狀態；JSON schema 驗證輸入格式，但不自動保證業務邏輯完整。

非同步平台先回 job ID，背景程序再推進工作。要分 HTTP request 成功、資料持久化成功和運算成功。主線只有 MPI 真實提交到 Kubernetes；其他 benchmark 名稱的分支仍有模擬行為。

現在 API 先建立 PostgreSQL metadata，再在 Redis transaction 發布 record 與 queue entry。這是兩個系統，沒有跨系統原子交易。手動 worker 端點在主 overlay 被關閉，教學不再以手動按 endpoint 推進工作。

## 目前環境與實測邊界

現行 GKE 主線；本機先用 mock 測試學習，不需要先拿雲端權限。

[本週實作／證據入口](<../evidence/automatic-worker-20260922.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：平台 API 設計](<day1-platform-api-design.md>)
- [Day2：REST 與端點契約](<day2-rest-api-design.md>)
- [Day3：Job identity](<day3-job-identity.md>)
- [Day4：Memory queue 的限制](<day4-memory-queue.md>)
- [Day5：API 映像與啟動](<day5-dockerize-api.md>)
- [Day6：API 監控與健康](<day6-monitoring-integration.md>)

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
