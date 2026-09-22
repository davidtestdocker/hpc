<!-- current-curriculum: 2026-09-22 -->
# Week18 Day2 — Bandwidth、latency、MTU

[上一課](<day1-linux-network-troubleshooting-baseline.md>) · [本週目錄](README.md) · [下一課](<day3-packet-level-network-failure-troubleshooting.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Bandwidth、latency、MTU」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

吞吐不足可能是 TCP、CPU、路徑或封包遺失，不是單純看 NIC 規格。MTU 不一致可能影響大封包路徑，但不能未量測就把所有 timeout 歸因給 MTU。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[benchmark/network/run_iperf3.sh](<../../benchmark/network/run_iperf3.sh>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```bash
# 效能測試腳本（run_iperf3）：讀取參數、執行測試並輸出結果；須在具備對應工具的環境執行。
# Shell 語法：${變數} 取值，${1:-預設值} 讀取參數並提供預設；$(...) 取得指令輸出。
# 行尾反斜線延續同一指令；| 把標準輸出傳給下一指令；> 覆寫檔案，>> 附加內容。

# 設定 Shell 錯誤處理；-e 遇未被處理的指令失敗時退出，pipefail 使管線反映其中的失敗。
set -e

SERVER=${1:-iperf3-server}
TIME=${2:-30}

echo "================================"
echo " Network Benchmark"
echo "================================"

echo "Server : ${SERVER}"
echo "Runtime: ${TIME}s"

echo ""

# 網路吞吐測試：-c 指定伺服器，-t 指定測試秒數。
iperf3 \
    -c ${SERVER} \
    -t ${TIME}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 iperf3 腳本，區分單 stream／多 stream 與延遲測試；用文字列出控制 endpoint、路徑、協定與持續時間的方式，不修改主 node MTU。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '2,24p' 'benchmark/network/run_iperf3.sh'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/network-policy-validation-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week18/day2-network-quality-bandwidth-latency-mtu.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
