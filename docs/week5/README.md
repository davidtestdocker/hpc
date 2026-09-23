# Week5 — 持久化與可恢復 worker

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week4](../week4/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

Redis job record 保存可供 worker 接續的狀態；queue 保存相容的工作 ID 清單。PostgreSQL 保存 metadata／status，兩者的資料用途不同，不要假設結果都在 DB。

Lease 是有期限的協調鎖，需要續期並檢查是否仍擁有它。固定 JobSet 名稱與 owner label 讓提交可重試，但不能推成整个平台 exactly-once。

流程為 accepted／retrying／processing → submitted → completed／failed。MPI collector 未取得終態就等待下一輪；done marker 標記清理已完成。程序重啟恢復依賴 Redis record 仍存在，與 Redis 資料全失後恢復是不同問題。

## 目前環境與實測邊界

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

## 本週材料怎麼讀

- **Day1～Day2：Redis 資料與持久化** — [api/main.py](../../api/main.py) 可看 job record 的寫入；[compose.yaml](../../compose.yaml) 可看 AOF 與資料 volume；[Redis Deployment](../../helm/redis/templates/deployment.yaml) 和 [PVC](../../helm/redis/templates/pvc.yaml) 是 Kubernetes 的對照設定。
- **Day3～Day5：處理、接續與重試** — [api/worker.py](../../api/worker.py) 可追工作狀態、lease 與失敗分支；[dispatcher.py](../../api/workloads/dispatcher.py) 可看 MPI 工作如何提交或接回既有 JobSet。
- **Day3～Day5 的保存結果** — [自動 worker 驗收 JSON](../evidence/automatic-worker-20260922.json) 記錄 queued／submitted 階段停啟接續，以及模擬失敗三次後 failed。它對應這三課的恢復與重試案例；不涵蓋 Redis 資料全失。
- **Day6～Day7：資料表與 Session** — [models.py](../../api/database/models.py) 看保存哪些欄位，[session.py](../../api/database/session.py) 看 Session 建立方式，再回 [api/main.py](../../api/main.py) 追 commit。

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
