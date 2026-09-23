# Week4 — API：提交工作不等於同步執行

現行教材版本：2026-09-22。先讀本頁，再按 Day 順序閱讀；不必先讀懂整個專案。

本週每日教材已完成逐篇文件核對。先讀各課頁首的修正與結果邊界，再讀完整原文；沒有 raw log 的課程不冒充實測。全套見[稽核清單](../audits/curriculum-content-audit.md)與[問題總表](../audits/curriculum-findings.md)。

## 先備與學習方式

先完成 [Week3](../week3/README.md)。遇到陌生名詞先回前週，不必邊猜邊背架構。 每一課先解釋概念，再直接讀現行補充、已保存結果與原本完整教學。原本完整教材與輸出已放回每一課下半部；前面是現行補充與已有結果，無須重新操作。

## 基礎解說

HTTP method 與 path 共同識別介面。POST 可建立工作，GET 查狀態；JSON schema 驗證輸入格式，但不自動保證業務邏輯完整。

非同步平台先回 job ID，背景程序再推進工作。要分 HTTP request 成功、資料持久化成功和運算成功。主線只有 MPI 真實提交到 Kubernetes；其他 benchmark 名稱的分支仍有模擬行為。

現在 API 先建立 PostgreSQL metadata，再在 Redis transaction 發布 record 與 queue entry。這是兩個系統，沒有跨系統原子交易。手動 worker 端點在主 overlay 被關閉，教學不再以手動按 endpoint 推進工作。

## 目前環境與實測邊界

現行 GKE 主線；直接讀保存結果與 mock 測試原始碼，不要求執行或取得雲端權限。

## 本週材料怎麼讀

- **Day1～Day3：API 與工作編號** — [api/main.py](../../api/main.py) 中的路由、`BenchmarkRequest`、`create_benchmark`，分別對應請求入口、輸入格式、建立 job ID 與回應。
- **Day4：工作如何保存** — 先讀課文的 `jobs={}`、`job_queue=[]` 舊範例，再對照 [api/main.py](../../api/main.py) 的 PostgreSQL／Redis 寫入。程序內清單與外部儲存的差異是本課重點。
- **Day5：API 如何啟動** — [docker/Dockerfile](../../docker/Dockerfile) 的 `CMD` 指定 Uvicorn 啟動 `api.main:app`；[compose.yaml](../../compose.yaml) 提供容器設定。
- **Day6：端點各自回什麼** — 在 [api/main.py](../../api/main.py) 找 `/health`、`/health/redis`、`/metrics` 與 `/job-metrics`，對照健康回應、依賴檢查、Prometheus 格式與工作數量 JSON。

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
