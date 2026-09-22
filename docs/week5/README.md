# Week5 — 持久化與可恢復 worker

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week4](../week4/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再對照目前檔案，最後做具體練習。完整舊教材已另外封存，新正文不再混入舊環境指令。

## 基礎解說

Redis job record 保存可供 worker 接續的狀態；queue 保存相容的工作 ID 清單。PostgreSQL 保存 metadata／status，兩者的資料用途不同，不要假設結果都在 DB。

Lease 是有期限的協調鎖，需要續期並檢查是否仍擁有它。固定 JobSet 名稱與 owner label 讓提交可重試，但不能推成整个平台 exactly-once。

流程為 accepted／retrying／processing → submitted → completed／failed。MPI collector 未取得終態就等待下一輪；done marker 標記清理已完成。程序重啟恢復依賴 Redis record 仍存在，與 Redis 資料全失後恢復是不同問題。

## 目前環境與實測邊界

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

[本週實作／證據入口](<../evidence/automatic-worker-20260922.json>)。本週的原始碼、manifest 與保存的成功／失敗各有不同證明力，不能全部當成今天又測過一次。

## 每日閱讀順序

- [Day1：Redis key、record 與 queue](<day1-redis-foundation.md>)
- [Day2：Redis 持久化](<day2-redis-persistence.md>)
- [Day3：現行 worker 狀態機](<day3-reliable-worker-state-machine.md>)
- [Day4：卡住與重啟接續](<day4-stuck-job-recovery.md>)
- [Day5：Retry 與 dead-letter](<day5-retry-strategy-and-deadletter-que.md>)
- [Day6：PostgreSQL 與交易邊界](<day6-postgresql-foundation.md>)
- [Day7：SQLAlchemy Session](<day7-sqlalchemy-foundation.md>)

## 練習分級

先做各課的唯讀／紙上推演，再選[本機練習](../current-environment.md)。需要建立資源、修改設定、壓測或恢復測試時，改走 runbook 並先確認目標；本教材不要求你一邊讀一邊操作正式叢集。

讀完本週應能以自己的話說出：概念解決什麼、程式／設定在哪、如何驗證、什麼尚未驗證。再進下一週，最後才用 README 串成整體架構。
