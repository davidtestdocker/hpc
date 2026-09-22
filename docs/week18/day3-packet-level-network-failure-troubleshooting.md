<!-- current-curriculum: 2026-09-22 -->
# Week18 Day3 — 封包級排障

[上一課](<day2-network-quality-bandwidth-latency-mtu.md>) · [本週目錄](README.md) · [下一課](<day4-kubernetes-network-troubleshooting.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「封包級排障」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

SYN 無回應、RST、完成握手後無應用資料代表不同失敗階段。抓包只證明所處觀測點看到什麼，沒看到封包不必然表示來源沒送。

## 在現在的專案中

本週可用 CPU 學主機網路；不把 CPU 測試或 Socket fallback 當 RDMA 硬體實測。

本課對照：[docs/evidence/network-policy-validation-20260921.json](<../evidence/network-policy-validation-20260921.json>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
  "result": "pass",
  "environment": {
    "cluster": "hpc-gpu-sg-rehearsal",
    "zone": "asia-southeast1-a",
    "lifecycle": "terraform apply then destroy",
    "network_policy": {
      "enabled": true,
      "provider": "CALICO"
    },
    "system_node": {
      "count": 1,
      "machine_type": "e2-standard-2",
      "ready": true
    },
    "gpu_node_count": 0
  },
  "test": {
    "namespace": "network-policy-validation",
    "server": "server:80",
    "policy": "allow-labeled-client-to-server",
    "baseline": {
      "allowed_client_exit_code": 0,
      "denied_client_exit_code": 0
    },
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 以服務未監聽與防火牆丟包兩種情境預測差異，對照 Calico allow／deny evidence；timeout 只支持不通，不單独证明是哪個設備丟棄。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '3,26p' 'docs/evidence/network-policy-validation-20260921.json'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/network-policy-validation-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week18/day3-packet-level-network-failure-troubleshooting.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
