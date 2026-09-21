#!/bin/bash
# 效能測試腳本（run_pgbench）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

HOST="postgres-service"
USER="hpc"
DB="pgbench"

CLIENTS=${1:-10}
THREADS=${2:-2}
TRANSACTIONS=${3:-100}

RESULT_DIR="./results"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

RESULT_FILE="${RESULT_DIR}/pgbench_${TIMESTAMP}.log"


# 建立結果目錄；-p 會建立缺少的父目錄，目錄存在時不報錯。
mkdir -p ${RESULT_DIR}


echo "================================"
echo " PostgreSQL Benchmark"
echo "================================"

echo "Host: ${HOST}"
echo "Database: ${DB}"
echo "Clients: ${CLIENTS}"
echo "Threads: ${THREADS}"
echo "Transactions/client: ${TRANSACTIONS}"

echo ""


# PostgreSQL 壓測：-h 主機、-U 帳號、-d 資料庫、-c 連線數、-j 執行緒、-t 每個 client 的交易數。
pgbench \
  -h ${HOST} \
  -U ${USER} \
  -d ${DB} \
  -c ${CLIENTS} \
  -j ${THREADS} \
  -t ${TRANSACTIONS} \
  | tee ${RESULT_FILE}



