<!-- current-curriculum: 2026-09-22 -->
# Week5 Day2 — Redis 持久化

[上一課](<day1-redis-foundation.md>) · [本週目錄](README.md) · [下一課](<day3-reliable-worker-state-machine.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Redis 持久化」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

PVC 使資料能跨 Pod 替換保存，AOF 是 Redis 的持久化機制；磁碟、程序與邏輯資料的故障範圍不同。PVC 不等於離線備份，也不保證任何資料遺失都可恢復。

## 在現在的專案中

主 overlay 啟用獨立 api-worker；手動 /worker/* 返回 409。

本課對照：[helm/redis/templates/deployment.yaml](<../../helm/redis/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
              mountPath: /data
          {{- end }}
      {{- if .Values.persistence.enabled }}
      volumes:
        - name: redis-data
          persistentVolumeClaim:
            claimName: {{ .Values.persistence.claimName }}
      {{- end }}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 對照 Deployment 的 /data volumeMount 與 PVC claimName，找啟動 AOF 的 command。讀保存的 Pod replacement 證據，別把它說成全失災難恢復。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '64,71p' 'helm/redis/templates/deployment.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/automatic-worker-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week5/day2-redis-persistence.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
