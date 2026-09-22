<!-- current-curriculum: 2026-09-22 -->
# Week8 Day4 — Helm 條件與共用命名

[上一課](<Day3_Helmize_Platform.md>) · [本週目錄](README.md) · [下一課](<Day5_Kustomize_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 先備知識與本課目標

先讀本週 README 的基礎解說，再依上方順序進入本課。目標是理解「Helm 條件與共用命名」，並能把概念對到實際檔案；第一次不要求先懂完整平台架構。

## 概念解說

if 可選擇是否產生資源，toYaml／nindent 把巢狀值以正確縮排輸出。模板空白控制可能影響 YAML，因此看原模板不足以保證渲染正確。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[helm/api/templates/worker.yaml](<../../helm/api/templates/worker.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
        {{- toYaml .Values.worker.nodeSelector | nindent 8 }}
      containers:
        - name: worker
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          # 覆寫映像預設的 Uvicorn 命令，啟動獨立 Python worker。
          command: ["python", "-m", "api.worker"]
          envFrom:
            # ConfigMap 提供服務位址與輪詢設定；密碼沿用外部建立的 Secret。
            - configMapRef:
                name: {{ include "api.fullname" . }}-config
            - secretRef:
                name: postgres-secret
          resources:
            # requests 供排程器計算容量，limits 限制容器 CPU／記憶體上限。
            {{- toYaml .Values.worker.resources | nindent 12 }}
{{- end }}
```

## 閱讀與練習

1. 從 repo 根目錄讀取下面指定區段，對照概念解說；遇到不熟名詞回本週基礎，不需要先記所有命令。
2. 比較 worker.enabled true／false 的離線輸出，檢查 worker 是否存在；再核對 API 和 worker 的命名與 ConfigMap 引用一致。
3. 記下你的觀察與理由，區分「從程式讀到」「本機執行看到」「歷史證據記錄」。沒有做過的實驗不要填成功數值。

```bash
sed -n '28,44p' 'helm/api/templates/worker.yaml'
```

這是唯讀檔案練習。需要實際測試時，依[現行練習與操作分級](../current-environment.md)選擇本機或離線步驟；部署、負載和故障注入另依 runbook 確認目標與影響。本次文件改寫沒有重新執行這些雲端操作。

## 怎樣判斷自己讀懂了

- 能完成上面的具體練習，指出對應欄位／函式，而不是只背工具名稱。
- 能解釋本課概念在什麼条件下成立，並分清設定存在與實測成功。
- 能從[本週證據／實作對照](<../evidence/platform-deployment-20260921.json>)找到相關依據；它是保存的紀錄或原始碼，不是即時可用性保證。

## 舊版與新版本的關係

[改寫前完整教材快照](<../history/20260922-before-current/week8/Day4_Helm_Advanced.md.txt>)保存原有教學、命令、輸出和版本註記，作為文字檔閱讀；它不是現行操作手冊。日期與環境仍依原文，不把舊結果改名成新驗收。保存規則與 SHA-256 見[歷史索引](../history/20260922-before-current/README.md)。
