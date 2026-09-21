#!/bin/bash
# 效能測試腳本（run_stress_ng）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

CPU_WORKERS=${1:-2}
TIMEOUT=${2:-60}

echo "================================"
echo " CPU Benchmark"
echo "================================"

echo "CPU Workers: ${CPU_WORKERS}"
echo "Duration: ${TIMEOUT}s"

echo ""

# CPU 壓測：--cpu 指定 worker 數，--timeout 指定持續時間，metrics 顯示量測統計。
stress-ng \
  --cpu ${CPU_WORKERS} \
  --timeout ${TIMEOUT}s \
  --metrics-brief
