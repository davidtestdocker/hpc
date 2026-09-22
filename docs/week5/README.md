# Week5 — 持久化與可恢復 worker

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

## 先備與學習方式

先完成 [Week4](../week4/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

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

## 直接讀結果，不要求重跑

每課的「已有結果與解讀」列出可用的已保存證據；「原始完整教材與當時輸出」保留整篇舊文。命令當作理解當時做法的材料，不需要你再開 VM 或在本機測試。沒有保存的實測結果會明說，示例不當作真實驗收。

讀到不熟的地方先回本週概念，再看輸出與解讀；不用自己重建環境找答案。
