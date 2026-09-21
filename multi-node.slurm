#!/bin/bash
# Slurm 批次工作：sbatch 讀取資源需求，取得 allocation 後執行下方 Shell 指令。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# Job name.
# SBATCH 是排程器指令，非普通說明註解：工作名稱，顯示於 squeue。
#SBATCH --job-name=multi-node-test

# Use the CPU partition.
# SBATCH 是排程器指令，非普通說明註解：指定使用的 Slurm 分區。
#SBATCH --partition=cpu

# Request two compute nodes.
# SBATCH 是排程器指令，非普通說明註解：申請節點數。
#SBATCH --nodes=2

# Run two tasks on each node.
# SBATCH 是排程器指令，非普通說明註解：每個節點執行的 task 數量。
#SBATCH --ntasks-per-node=2

# SBATCH 是排程器指令，非普通說明註解：工作開始後使用的目錄。
#SBATCH --chdir=/tmp

# Save output using the job ID.
# SBATCH 是排程器指令，非普通說明註解：標準輸出檔案；%j 由 Slurm 替換為 job ID。
#SBATCH --output=multi-node-%j.out


# Show Slurm allocation information.
echo "JOB_ID=$SLURM_JOB_ID"
echo "NODELIST=$SLURM_JOB_NODELIST"
echo "NTASKS=$SLURM_NTASKS"

# Launch one hostname command per Slurm task.
# 在已分配的 Slurm 資源中啟動 task，通常每個 task 執行一次此命令。
srun hostname
