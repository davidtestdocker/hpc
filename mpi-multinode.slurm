#!/bin/bash
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
mpirun \
  --allow-run-as-root \
  --host compute-01:2,compute-02:2 \
  -np 4 \
  /tmp/mpi_hello
