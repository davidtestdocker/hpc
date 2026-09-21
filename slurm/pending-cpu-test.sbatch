#!/bin/bash
# Slurm 批次工作：sbatch 讀取資源需求，取得 allocation 後執行下方 Shell 指令。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。
# SBATCH 是排程器指令，非普通說明註解：工作名稱，顯示於 squeue。
#SBATCH --job-name=pending-cpu-test
# SBATCH 是排程器指令，非普通說明註解：指定使用的 Slurm 分區。
#SBATCH --partition=cpu
# SBATCH 是排程器指令，非普通說明註解：每個 task 配置的 CPU 數量。
#SBATCH --cpus-per-task=1
# SBATCH 是排程器指令，非普通說明註解：每個節點要求的記憶體。
#SBATCH --mem=256M
# SBATCH 是排程器指令，非普通說明註解：最長執行時間，格式為時:分:秒。
#SBATCH --time=00:10:00

hostname
sleep 300
