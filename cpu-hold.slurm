#!/bin/bash
# Slurm 批次工作：sbatch 讀取資源需求，取得 allocation 後執行下方 Shell 指令。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# Job name.
# SBATCH 是排程器指令，非普通說明註解：工作名稱，顯示於 squeue。
#SBATCH --job-name=cpu-hold

# Use the debug partition.
# SBATCH 是排程器指令，非普通說明註解：指定使用的 Slurm 分區。
#SBATCH --partition=debug

# Request one node.
# SBATCH 是排程器指令，非普通說明註解：申請節點數。
#SBATCH --nodes=1

# Request all 4 CPU tasks on this node.
# SBATCH 是排程器指令，非普通說明註解：申請 task 數量；task 不一定等同執行緒。
#SBATCH --ntasks=4

# Save output using the Slurm job ID.
# SBATCH 是排程器指令，非普通說明註解：標準輸出檔案；%j 由 Slurm 替換為 job ID。
#SBATCH --output=cpu-hold-%j.out


# Show basic job information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NTASKS=$SLURM_NTASKS"
echo "NODE=$(hostname)"

# Launch 4 tasks.
# Each task sleeps for 60 seconds to keep resources occupied.
# 在已分配的 Slurm 資源中啟動 task，通常每個 task 執行一次此命令。
srun sleep 60
