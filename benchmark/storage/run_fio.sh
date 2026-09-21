#!/bin/bash
# 效能測試腳本（run_fio）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

SIZE=${1:-1G}
RUNTIME=${2:-60}

echo "================================"
echo " Storage Benchmark"
echo "================================"

echo "Test Size: ${SIZE}"
echo "Runtime: ${RUNTIME}s"

echo ""

# 儲存壓測：size 設定檔案大小、rw 指定讀寫模式、bs 設定區塊大小、direct 避開頁面快取。
fio \
  --name=storage-test \
  --filename=/tmp/fio-test-file \
  --size=${SIZE} \
  --rw=readwrite \
  --bs=4k \
  --direct=1 \
  --runtime=${RUNTIME} \
  --time_based \
  --group_reporting
