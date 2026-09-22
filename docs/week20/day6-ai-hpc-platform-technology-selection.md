<!-- current-curriculum: 2026-09-22 -->
# Week20 Day6 — 架構選型與整體說明

[上一課](<day5-ai-hpc-production-troubleshooting.md>) · [本週目錄](README.md) · [整體展示](../../README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「架構選型與整體說明」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

FastAPI 接請求、Redis 保存接續 record、PostgreSQL 保存 metadata、Kueue 准入、JobSet 管理 MPI 群組；獨立 runner 做訓練。跨 DB 雙寫與結果儲存邊界仍在，不靠增加工具掩蓋。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[docs/architecture/platform-architecture.md](<../architecture/platform-architecture.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

````text
## Main Platform Flow

```mermaid
flowchart TD
    CLIENT["Client"]
    subgraph SERVICES["Platform service layer — system-pool"]
        API["FastAPI"]
        DB["PostgreSQL — initial job metadata"]
        QUEUE["Redis — job state / job_queue"]
        WORKER["api-worker — background polling / collector"]
    end
    subgraph ORCHESTRATION["Kubernetes resource orchestration"]
        KAPI["Kubernetes API"]
        JS["JobSet — distributed job lifecycle grouping"]
        KUEUE["Kueue — queue / quota / resource admission / TAS"]
        SCHED["Kubernetes Scheduler — Pod placement"]
    end
    subgraph COMPUTE["Distributed / GPU workload layer — gpu-pool"]
        LAUNCHER["MPI Launcher × 1"]
        WORKERS["MPI Workers × 3"]
        RANKS["mpirun — MPI ranks 0 / 1 / 2"]
    end
    CLIENT -->|"POST /benchmark"| API
    API -->|"insert initial metadata"| DB
````

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 最後讀整體架構與 README，用兩分鐘說出主線、獨立實驗和限制。若要改 workload／規模，指出需重新驗證哪些假設，而不是宣稱一套配置適用所有 HPC。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '15,38p' 'docs/architecture/platform-architecture.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week20/day6-ai-hpc-platform-technology-selection.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
