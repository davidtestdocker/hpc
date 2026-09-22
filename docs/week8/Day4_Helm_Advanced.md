<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day4 — Helm 條件與共用命名

[上一課](<Day3_Helmize_Platform.md>) · [本週目錄](README.md) · [下一課](<Day5_Kustomize_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day4_Helm_Advanced.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 overlay 是 gpu-sg-platform；Argo dev 仍指 overlays/dev，不能宣稱主環境已完成 GitOps 對齊。
> **閱讀順序**：先學本文基礎，再讀[Week8 現行對照與檢核](../learning-guide.md#week8)及[對應現行入口](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week8 Day4 - Helm Advanced

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [helm/api/Chart.yaml](../../helm/api/Chart.yaml)
- [helm/api/templates/_helpers.tpl](../../helm/api/templates/_helpers.tpl)
- [helm/api/templates/deployment.yaml](../../helm/api/templates/deployment.yaml)
- [helm/api/values.yaml](../../helm/api/values.yaml)

---

## 本日成果

完成 Helm Release 管理與 Helm Helper（`_helpers.tpl`）的學習，平台正式具備企業級 Helm Chart 的基本架構。

---

# 今日目標

完成 Helm 的核心能力：

* Helm Install
* Helm Upgrade
* Helm History
* Helm Rollback
* Helper Template
* define
* include

---

# Helm 與 kubectl 的角色

Helm：

負責：

* Chart
* Release
* Revision
* Values
* 部署管理

kubectl：

負責：

* Pod
* Deployment
* Service
* Log
* Debug
* Cluster 狀態

因此：

部署：

```bash
helm upgrade api ./api -n hpc-platform
```

驗證：

```bash
kubectl get pods -n hpc-platform
```

查看 Log：

```bash
kubectl logs -n hpc-platform deployment/api
```

---

# Helm Install

第一次部署：

```bash
helm install api ./api -n hpc-platform
```

建立：

Release：

```text
api
```

---

# Helm Upgrade

修改：

```yaml
replicaCount
```

更新：

```bash
helm upgrade api ./api -n hpc-platform
```

Helm：

自動比較差異。

更新 Kubernetes Resource。

---

# Helm History

查看：

```bash
helm history api -n hpc-platform
```

平台：

完成：

```text
Revision1

↓

Revision2

↓

Revision3

↓

Revision4
```

完整保留部署歷史。

---

# Helm Rollback

Rollback：

```bash
helm rollback api 2 -n hpc-platform
```

注意：

Rollback：

不是：

回到 Revision2。

而是：

建立：

新的：

```text
Revision4
```

內容：

等同：

Revision2。

History：

永遠保留。

方便：

Audit。

---

# Release

目前：

Release：

```text
api
```

Chart：

```text
api
```

Chart：

可以建立：

多個：

Release。

例如：

```text
api

api-dev

api-stage

api-prod
```

互不影響。

---

# _helpers.tpl

Helm：

提供：

```text
_helpers.tpl
```

作為：

共用 Template。

避免：

每個 YAML：

重複相同內容。

---

# define

建立：

Helper：

例如：

```tpl
{{ define "api.labels" }}
...
{{ end }}
```

建立：

可重複使用 Template。

---

# include

使用：

Helper：

```tpl
{{ include "api.labels" . }}
```

如同：

Python：

```python
function()
```

概念。

---

# selectorLabels

Deployment：

Selector：

```yaml
matchLabels:
```

Pod：

Labels：

```yaml
labels:
```

Service：

Selector：

```yaml
selector:
```

全部：

改為：

```tpl
{{ include "api.selectorLabels" . }}
```

避免：

Selector 不一致。

---

# labels

Deployment：

Metadata：

Labels：

改為：

```tpl
{{ include "api.labels" . }}
```

由：

Helper：

統一管理。

---

# fullname

平台：

開始使用：

```tpl
{{ include "api.fullname" . }}
```

建立：

Resource Name。

例如：

Service：

```text
api-service
```

ConfigMap：

```text
api-config
```

Secret：

```text
api-secret
```

未來：

若：

Release：

改為：

```text
api-dev
```

Render：

自動變成：

```text
api-dev-service

api-dev-config

api-dev-secret
```

避免：

不同 Release：

互相衝突。

---

# Helper 化資源

目前：

完成：

* Deployment Labels
* Deployment Selector
* Pod Labels
* Service Selector
* ConfigMap Name
* Secret Name
* Service Name

開始使用：

Helper。

---

# Helm Chart 能力提升

目前 Chart：

已具備：

* Values 管理
* Helper Template
* Release Name
* Dynamic Resource Name
* Dynamic Selector
* Dynamic Labels

開始符合企業 Helm Chart 設計方式。

---

# 今日重點

Helm：

不是：

取代 kubectl。

Helm：

負責：

Release。

kubectl：

負責：

Cluster。

企業：

日常流程：

```text
helm upgrade

↓

kubectl rollout status

↓

kubectl get pods

↓

kubectl logs
```

---

# Interview Q&A

## Q1：Helm Rollback 為什麼會建立新的 Revision？

Rollback 不會修改歷史，而是重新部署指定 Revision 的內容，因此會建立新的 Revision，保留完整部署紀錄。

---

## Q2：為什麼需要 `_helpers.tpl`？

將名稱、Labels、Selector 等共用邏輯集中管理，避免重複並提升 Helm Chart 的可維護性。

---

## Q3：Helm 與 kubectl 的差別？

Helm 負責 Chart、Release 與版本管理；kubectl 負責操作及觀察 Kubernetes Cluster 中的實際資源。

---

# 今日成果

平台已完成：

* Helm Release 管理
* Helm History
* Helm Rollback
* Helper Template
* define
* include
* Dynamic Labels
* Dynamic Selector
* Dynamic Resource Name

Helm Chart 已具備企業實務中常見的設計模式。

---

# 下一步

Week8 Day5：

Kustomize

學習：

* Base
* Overlay
* Patch
* Strategic Merge
* JSON6902 Patch
* dev / stage / prod 環境管理
* 與 Helm 的搭配方式
