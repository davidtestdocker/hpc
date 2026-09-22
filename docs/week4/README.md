# Week4 — API：提交工作不等於同步執行

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week3](../week3/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

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

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
