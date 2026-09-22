<!-- current-curriculum: 2026-09-22 -->
# Week1 Day6 — Disk I/O

[上一課](<day5-memory.md>) · [本週目錄](README.md) · [下一課](<day7-performance-analysis.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Disk I/O」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

df 回答空間是否足夠，不直接回答存取延遲；磁碟忙還要分隨機／循序、讀／寫與 queue depth。Redis 資料放在容器可寫層或 PVC，生命週期不同。

## 在現在的專案中

本週在自己的 Linux 學習環境做唯讀觀察，不聲稱主叢集當下健康。

本課對照：[helm/redis/templates/pvc.yaml](<../../helm/redis/templates/pvc.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  accessModes:
    # ReadWriteOnce 限制讀寫掛載於單一 node，不是「只有一個 Pod」的鎖。
    - ReadWriteOnce
  resources:
    requests:
      storage: {{ .Values.persistence.size }}
{{- end }}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 先用 df -h 觀察自己的檔案系統，再讀 Redis PVC 的容量與掛載設計。不要用清空資料或大量寫入測試當成第一個排查動作。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '10,16p' 'helm/redis/templates/pvc.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week1/day6-disk-io.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
