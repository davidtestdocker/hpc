<!-- current-curriculum: 2026-09-22 -->
# Week7 Day6 — Ingress 與 Controller

[上一課](<Day5_Service_Types_NodePort.md>) · [本週目錄](README.md) · [下一課](<Day7_Horizontal_Pod_Autoscaler.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Ingress 與 Controller」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

Ingress 是路由宣告，需要 controller 處理；host rule、TLS、DNS 是不同設定。歷史 Traefik 範例存在，不代表目前 GKE 主平台有可公開存取的同名網域。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/templates/ingress.yaml](<../../helm/api/templates/ingress.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
{{- if .Values.ingress.enabled }}

# 資源所屬 API 群組與版本；Helm Chart 中則是 Chart 格式版本。
apiVersion: networking.k8s.io/v1
# 資源種類，決定由哪個 Kubernetes 控制器或工具處理。
kind: Ingress

# 資源識別資訊；name 與 namespace 決定命名空間內的身分。
metadata:
  name: {{ include "api.fullname" . }}-ingress
  # 資源所屬命名空間；叢集層級資源不使用此欄位。
  namespace: {{ .Release.Namespace }}

# 期望狀態；控制器據此建立或調整實際資源。
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}

  # 規則清單；RBAC 中定義 API 存取權限，Ingress 中定義路由。
  rules:
    - host: {{ .Values.ingress.host | quote }}
      http:
        paths:
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 讀 Ingress 的 host／backend，再找 values 的 enabled。把「模板存在」「已渲染」「controller 生效」「流量成功」分成四項。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '4,27p' 'helm/api/templates/ingress.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-after-training-20260922.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week7/Day6_Ingress_Traefik.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
