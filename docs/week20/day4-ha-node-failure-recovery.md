<!-- current-curriculum: 2026-09-22 -->
# Week20 Day4 — 恢復與 HA 邊界

[上一課](<day3-networkpolicy-tenant-isolation.md>) · [本週目錄](README.md) · [下一課](<day5-ai-hpc-production-troubleshooting.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「恢復與 HA 邊界」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

worker 停止期間 JobSet 可繼續跑，恢復後收回終態；Redis Pod replacement 證明 PVC 上的測試 key 保留。這兩項都不代表整台 node 消失後有另一台接手。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[docs/demo/platform-recovery-20260921.md](<../demo/platform-recovery-20260921.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
# 2026-09-21 平台修復與驗收

本輪是現有 GKE `hpc-gpu-sg` 的維護實測，非從零重建或 production HA 認證。

## 1. Controller 排程容量

JobSet v0.12.0 controller Pending；system node allocatable 1930m，既有 requests 1638m，剩餘 292m 小於 controller request 500m。
即時 CPU 用量樣本為 198m。套用 [demo patch](../../k8s/controllers/jobset-demo-resources-patch.yaml)，將 request 調為 100m、綁定 system-pool，保留原記憶體配置與未設 CPU limit 的行為。
controller 恢復 1/1 Running，之後用量樣本為 4m／18Mi。[修復前](../evidence/platform-preflight-20260921.json)／[修復後](../evidence/platform-preflight-after-20260921.json) 保存前置檢查結果。

這些是低負載 demo 樣本，沒有證明大規模 workload 下 100m 足夠。沒有改 GKE 系統元件 requests，也沒有新增 VM。

## 2. Redis 持久化與恢復

舊 Redis 雖開啟 AOF，卻沒有掛載 volume。實測所有 DB 為空後，工具停止 API、暫停 source writes、再次驗空、建立 PVC 並部署 Redis。
寫入測試 key 後執行 graceful Pod replacement，確認 key 仍存在，再移除測試 key 並恢復 API。

[JSON 紀錄](../evidence/redis-persistence-migration-20260921.json) 顯示：

- 維護開始：09:24:20 UTC。
- 新 Redis ready、PVC Bound：09:24:41 UTC。
- Pod 替換後 test key 保留：09:24:55 UTC。
- API 恢復完成：09:25:12 UTC。

```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照 9/22 worker restart、9/21 Redis 以及歷史 JobSet recovery，逐一寫故障點、觀察、恢復動作、限制；保留舊 TAS 恢復失敗事實。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '1,24p' 'docs/demo/platform-recovery-20260921.md'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week20/day4-ha-node-failure-recovery.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
