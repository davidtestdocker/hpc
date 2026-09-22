<!-- current-curriculum: 2026-09-22 -->
# Week17 Day4 — Slurm 多節點 CPU 案例

[上一課](<day3-hpc-communication-stack.md>) · [本週目錄](README.md) · [下一課](<day5-ray-kuberay-distributed-computing.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Slurm 多節點 CPU 案例」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

partition 組織節點，allocation 分配資源，task 數與 node 數不同。現有歷史案例有兩台 CPU VM 的 MPI，但計算 VM 後來被移除，不能直接使用舊節點名重跑。

## 在現在的專案中

Slurm／Ray 是獨立實驗教材與已保存歷史案例，不當作目前可用服務。

本課對照：[mpi-multinode.slurm](<../../mpi-multinode.slurm>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
# Slurm 批次工作：sbatch 讀取資源需求，取得 allocation 後執行下方 Shell 指令。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# SBATCH 是排程器指令，非普通說明註解：工作名稱，顯示於 squeue。
#SBATCH --job-name=mpi-multinode
# SBATCH 是排程器指令，非普通說明註解：指定使用的 Slurm 分區。
#SBATCH --partition=cpu
# SBATCH 是排程器指令，非普通說明註解：申請節點數。
#SBATCH --nodes=2
# SBATCH 是排程器指令，非普通說明註解：每個節點執行的 task 數量。
#SBATCH --ntasks-per-node=2
# SBATCH 是排程器指令，非普通說明註解：工作開始後使用的目錄。
#SBATCH --chdir=/tmp
# SBATCH 是排程器指令，非普通說明註解：標準輸出檔案；%j 由 Slurm 替換為 job ID。
#SBATCH --output=/tmp/mpi-multinode-%j.out

# Show Slurm allocation information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NODELIST=$SLURM_JOB_NODELIST"
echo "NTASKS=$SLURM_NTASKS"

# Launch 4 MPI ranks across two compute nodes.
# 啟動 MPI 程序；-np 指定 rank 數，--host 指定主機與 slots，需各主機都有相同執行檔。
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 Slurm demo 的成功 baseline 和 node failure 邊界，再看 sbatch 的 nodes／tasks；解釋 allocation 成功為何仍可能 MPI launcher 失敗。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '2,25p' 'mpi-multinode.slurm'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week17/day4-slurm-multinode-hpc-cluster.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
