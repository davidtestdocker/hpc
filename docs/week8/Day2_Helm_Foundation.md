<!-- current-curriculum: 2026-09-22 -->
# Week8 Day2 — Helm 的 values 與模板

[上一課](<Day1_GitOps_Foundation.md>) · [本週目錄](README.md) · [下一課](<Day3_Helmize_Platform.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Helm 的 values 與模板」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

.Values 讀 chart 設定，.Release 帶入 release 資訊，include 可共用命名模板。模板中的大括號不是合法的最終 Kubernetes 欄位，要先 render 才能判讀。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
# Helm 的 if 只在 worker.enabled=true 時渲染此資源；操作見自動 worker runbook。
{{- if .Values.worker.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api.fullname" . }}-worker
  namespace: {{ .Release.Namespace }}
spec:
  # Demo 使用一個副本；每筆工作的 Redis lease 額外提供重複處理協調。
  replicas: 1
  strategy:
    # Recreate 先停舊版再啟新版，避免小型 system-pool 承擔升級 surge 容量。
    type: Recreate
  selector:
    # selector 與下方 Pod labels 相符，讓 Deployment 管理自己的 worker Pods。
    matchLabels:
      app: {{ include "api.fullname" . }}-worker
  template:
    metadata:
      labels:
        app: {{ include "api.fullname" . }}-worker
    spec:
      # 沿用 namespace 最小 RBAC 身分，允許建立／讀取 JobSet 與回收 launcher log。
      serviceAccountName: {{ .Values.worker.serviceAccountName }}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 worker 的 if 條件與 image，對照主 overlay values；用 helm template 離線查看啟用 worker 時產生哪個 Deployment，不執行 install。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '2,25p' 'helm/api/templates/worker.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-deployment-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week8/Day2_Helm_Foundation.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
