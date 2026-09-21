#!/bin/bash
# 效能測試腳本（run_all）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -euo pipefail

RESULT_DIR="results/$(date +%Y%m%d_%H%M%S)"
# 建立結果目錄；-p 會建立缺少的父目錄，目錄存在時不報錯。
mkdir -p "${RESULT_DIR}"

# 定義共用函式；$1、$2、$3 分別接收名稱、命令字串與 log 檔名。
run_benchmark() {
    NAME=$1
    COMMAND=$2
    LOG_FILE=$3

    echo ""
    echo "======================================"
    echo "${NAME}"
    echo "======================================"

    # eval 由 Shell 再解析命令字串；2>&1 合併標準錯誤，tee 同時顯示與寫入 log。
    # if 根據管線退出狀態判斷 PASS／FAIL；pipefail 可避免 tee 成功掩蓋 benchmark 失敗。
    if eval "${COMMAND}" 2>&1 | tee "${RESULT_DIR}/${LOG_FILE}"; then
        echo "[PASS] ${NAME}"
    else
        echo "[FAIL] ${NAME}"
        echo ""
        echo "Benchmark stopped because ${NAME} failed."
        exit 1
    fi
}

echo "======================================"
echo " HPC AI Benchmark Framework"
echo "======================================"

echo ""
echo "Result Directory:"
echo "${RESULT_DIR}"

run_benchmark \
    "CPU Benchmark" \
    "bash cpu/run_stress_ng.sh 2 30" \
    "cpu.log"

run_benchmark \
    "Storage Benchmark" \
    "bash storage/run_fio.sh 1G 30" \
    "storage.log"

run_benchmark \
    "PostgreSQL Benchmark" \
    "bash postgres/run_pgbench.sh 10 2 100" \
    "postgres.log"

run_benchmark \
    "Network Benchmark" \
    "bash network/run_iperf3.sh iperf3-server 30" \
    "network.log"

echo ""
echo "======================================"
echo " Benchmark Summary"
echo "======================================"

echo "CPU          PASS"
echo "Storage      PASS"
echo "PostgreSQL   PASS"
echo "Network      PASS"

echo ""
echo "Result Directory: ${RESULT_DIR}"
echo "All benchmarks completed successfully."
