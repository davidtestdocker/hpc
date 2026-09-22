<!-- current-curriculum: 2026-09-22 -->
# Week11 Day1 — Prometheus 與資源分工

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2-Prometheus-ScrapeJob-Target與PullModel.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Prometheus 與資源分工」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

監控本身消耗 CPU、RAM、儲存，與被測工作共用節點時可能互相影響。舊 observability-pool 屬不同環境設計；現行 system-pool 的存在不能證明舊監控都已搬過來。

## 在現在的專案中

監控 manifests 和歷史 dashboard 保留為獨立路徑；不宣稱即時 target 健康。

本課對照：[helm/prometheus/templates/deployment.yaml](<../../helm/prometheus/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
spec:
  # 期望副本數；設定為 0 表示不維持執行中的副本。
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: Recreate
  # 選取要關聯的物件；不同資源種類支援的 selector 格式不同。
  selector:
    # 以完全相等的標籤鍵值選取物件。
    matchLabels:
      {{- include "prometheus.selectorLabels" . | nindent 6 }}
  # 子物件模板；控制器以此內容建立 Pod 或相關工作資源。
  template:
    metadata:
      #只要configmap.yaml內容有變 sha256sum就會變，所以就會偵測到prometheus的deployment有變，就會建新的prometheus pod
      # 附加設定或提示，由對應控制器解讀，不等同 selector 標籤。
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "prometheus.selectorLabels" . | nindent 8 }}
    spec:
      # Pod 使用的 ServiceAccount；RBAC 依此身分授予 API 權限。
      serviceAccountName: prometheus
      #這個 Pod 掛載的 Volume（PVC）都套用這個權限設定
      # 程序身分、權限與作業系統安全設定。
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 從 Prometheus Deployment 找 storage、resources、nodeSelector，逐项核對實際宣告；不要把舊 node pool 名稱帶成當前部署結論。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '15,38p' 'helm/prometheus/templates/deployment.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/README.md>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week11/Day1-建立Prometheus監控平台與Observability-Node-Pool.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
