<!-- current-curriculum: 2026-09-22 -->
# Week17 Day1 — MPI rank 與 launcher

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-mpi-performance-benchmark.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「MPI rank 與 launcher」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

MPI_Comm_rank 取得本程序編號，MPI_Comm_size 取得群組大小。hostname 讓你知道程序所在 host，但容器 hostname 不必然等於實體 node 名稱。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[mpi_hello.c](<../../mpi_hello.c>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```c
    MPI_Init(&argc, &argv);


    int world_size;
    int world_rank;


    /*
     * 取得 MPI communicator 裡總共有多少 process
     *
     * MPI_COMM_WORLD:
     * 代表目前所有 MPI process 的集合。
     *
     * 例如：
     * mpirun -np 4
     *
     * world_size = 4
     *
     * 代表目前有：
     * Rank 0
     * Rank 1
     * Rank 2
     * Rank 3
     */
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 mpi_hello.c，再對照現行 template 的 mpirun -np 與 worker 副本。確認 rank 0／1／2 是三個程序，不把 launcher 另算一個 MPI rank。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '21,44p' 'mpi_hello.c'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day1-mpi-fundamentals.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
