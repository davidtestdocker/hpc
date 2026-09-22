<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day7 — 多環境與 Argo 邊界

[上一課](<Day6-Helm-Kustomize-Integration.md>) · [本週目錄](README.md) · [下一週](../week9/README.md) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

不同 namespace 不代表完全隔離：cluster-scoped 資源、node、配額可能共享。dev／stage／prod 設定目前是 GitOps 教材，不能宣稱三環境都已驗證最新 worker。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[argocd/application-dev.yaml](<../../argocd/application-dev.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  syncPolicy:
  #automated 是不用手動按sync只要有差異(push完)就會同步
  #prune true 如果git沒有這檔案但cluster 有的話檔案也會刪除變成跟git一樣
  #selfHeal 假設有人編輯了replicas數量 但是git沒變的話 argocd會發現差異自動改回git上的數量 (不用等push)
    automated:
      # 同步時是否刪除 Git 中已移除的受管資源。
      prune: true
      # 是否自動修正叢集狀態與 Git 宣告之間的偏差。
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day7-GitOps_Multi_Environment_Integration.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 overlay 是 gpu-sg-platform；Argo dev 仍指 overlays/dev，不能宣稱主環境已完成 GitOps 對齊。
> **閱讀順序**：先學本文基礎，再讀[Week8 現行對照與檢核](../learning-guide.md#week8)及[對應現行入口](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week8 Day7 - GitOps Multi Environment Integration

> 現行入口（2026-09-21）：[平台部署與驗收](../runbooks/platform-bootstrap.md)。主 overlay 已使用獨立 values；本文 dev GitOps／CI 仍屬歷史路徑，不會自動更新新的主環境 image tag。

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [argocd/application-dev.yaml](../../argocd/application-dev.yaml)
- [argocd/application-prod.yaml](../../argocd/application-prod.yaml)
- [argocd/application-stage.yaml](../../argocd/application-stage.yaml)
- [argocd/project.yaml](../../argocd/project.yaml)
- [helm/api/values-dev.yaml](../../helm/api/values-dev.yaml)
- [helm/api/values-prod.yaml](../../helm/api/values-prod.yaml)
- [helm/api/values-stage.yaml](../../helm/api/values-stage.yaml)
- [kustomize/overlays/dev/deployment-patch.yaml](../../kustomize/overlays/dev/deployment-patch.yaml)
- [kustomize/overlays/dev/kustomization.yaml](../../kustomize/overlays/dev/kustomization.yaml)
- [kustomize/overlays/prod/deployment-patch.yaml](../../kustomize/overlays/prod/deployment-patch.yaml)
- [kustomize/overlays/prod/kustomization.yaml](../../kustomize/overlays/prod/kustomization.yaml)
- [kustomize/overlays/stage/deployment-patch.yaml](../../kustomize/overlays/stage/deployment-patch.yaml)
- [kustomize/overlays/stage/kustomization.yaml](../../kustomize/overlays/stage/kustomization.yaml)

---

## 學習目標

完成 GitOps 多環境平台整合，建立 Dev、Stage、Prod 三套獨立環境，透過 Helm、Kustomize、Argo CD 與 Traefik 完成完整的 GitOps 部署流程，並驗證實際流量經過 Ingress Controller 成功到達 API。

---

# 完成成果

✅ Dev Environment

✅ Stage Environment

✅ Prod Environment

✅ Argo CD Multi Application

✅ Multi Namespace Deployment

✅ Helm Values Environment Configuration

✅ Traefik Ingress Routing

✅ GitOps Auto Sync

✅ Host-based Routing Validation

---

# GitOps 架構

```
Git Repository

        │

        ▼

Argo CD

        │

        ▼

Kustomize Overlay

        │

        ▼

Helm Chart

        │

        ▼

Kubernetes
```

Git Repository 為唯一事實來源（Single Source of Truth）。

Argo CD 持續監控 Git Repository。

Repository 發生變更時：

```
Git Push

↓

Argo CD Detect

↓

Helm Render

↓

Kustomize Overlay

↓

Apply

↓

Kubernetes
```

完成自動同步。

---

# Multi Environment

建立三套完全獨立環境。

## Dev

Namespace

```
hpc-platform-dev
```

Image

```
hpc-ai-benchmark-platform-api:dev
```

Host

```
api-dev.hpc.local
```

---

## Stage

Namespace

```
hpc-platform-stage
```

Image

```
hpc-ai-benchmark-platform-api:stage
```

Host

```
api-stage.hpc.local
```

---

## Prod

Namespace

```
hpc-platform-prod
```

Image

```
hpc-ai-benchmark-platform-api:v1.0.0
```

Host

```
api-prod.hpc.local
```

三個環境完全隔離。

每個 Namespace 都擁有自己的：

- Deployment
- Service
- Ingress
- Redis
- PostgreSQL
- HPA

---

# Helm

Helm 負責管理所有可參數化設定。

例如：

```
Image Tag

Service Type

Ingress Host

Resources

Replica Count（HPA 關閉時）

HPA
```

各環境透過：

```
values-dev.yaml

values-stage.yaml

values-prod.yaml
```

即可產生不同 Deployment。

---

# Kustomize

Kustomize 負責：

```
Namespace

Helm Chart

Deployment Patch
```

不再使用：

```
Ingress Patch
```

原因：

Ingress 的：

```
spec.rules
```

屬於 List。

Strategic Merge Patch

會 Replace 整個 List。

造成：

```
http

paths

backend
```

全部消失。

因此：

Ingress Host

改由 Helm Values 管理。

---

# Argo CD

建立三個 Application。

```
hpc-dev

hpc-stage

hpc-prod
```

全部狀態：

```
Synced

Healthy
```

Git Push 後：

Argo CD 自動同步。

不需要：

```
kubectl apply
```

---

# Traefik

Traefik

=

Ingress Controller

負責：

讀取 Kubernetes Ingress。

建立 Routing Table。

依照：

```
Host

+

Path
```

決定流量轉送位置。

Traefik 本身不是 Ingress。

Ingress 是規則。

Traefik 是真正負責執行規則的 Controller。

---

# Ingress

每個環境都有自己的 Host。

Dev

```
api-dev.hpc.local
```

Stage

```
api-stage.hpc.local
```

Prod

```
api-prod.hpc.local
```

Ingress 依照 Host

轉送到對應 Namespace 的 Service。

---

# Service

Service 不直接知道 Pod IP。

Service 透過：

```
Selector
```

找到符合 Label 的 Pod。

Kubernetes 建立：

```
Endpoint
```

紀錄真正 Pod IP。

Service

↓

Endpoint

↓

Pod

---

# 流量流程

```
Browser / curl

↓

DNS

(/etc/hosts)

↓

Traefik

↓

Ingress

↓

Service

↓

Endpoint

↓

API Pod

↓

FastAPI
```

例如：

```
curl http://api-dev.hpc.local
```

完整流程：

```
api-dev.hpc.local

↓

Traefik

↓

Ingress

↓

api-service

↓

Endpoint

↓

API Pod

↓

GET /

↓

Response
```

---

# 驗證

確認 Argo CD

```bash
kubectl get application -n argocd
```

Expected

```
Synced

Healthy
```

---

確認 Ingress

```bash
kubectl get ingress -A
```

Expected

```
api-dev.hpc.local

api-stage.hpc.local

api-prod.hpc.local
```

---

確認 API

```bash
curl http://api-dev.hpc.local

curl http://api-stage.hpc.local

curl http://api-prod.hpc.local
```

Expected

```
{"message":"HPC API DEV","status":"running"}

{"message":"HPC API STAGE","status":"running"}

{"message":"HPC API PROD","status":"running"}
```

---

# 本日踩坑

## 問題一

使用 Kustomize Patch

修改：

```
Ingress Host
```

導致：

```
http

paths

backend
```

全部消失。

原因：

```
spec.rules
```

屬於 List。

Strategic Merge Patch

直接 Replace 整個 List。

---

## 解決方式

Host

改由：

```
Helm Values
```

管理。

Render 後：

```
Helm

↓

完整 Ingress

↓

Kustomize

↓

保留 http.paths
```

避免 Patch 導致 Rule 遺失。

---

# 本日重點

1.

Helm

負責：

所有可參數化設定。

---

2.

Kustomize

負責：

Environment Overlay。

---

3.

Argo CD

負責：

GitOps 自動同步。

---

4.

Traefik

負責：

Ingress Routing。

---

5.

Service

透過 Endpoint

找到真正 Pod。

---

6.

Ingress Host

應由 Helm Values 管理。

不要使用 Strategic Merge Patch 修改 List。

---

# Interview Q&A

## Q1

GitOps 中 Helm、Kustomize、Argo CD 三者如何分工？

Helm 負責模板與參數化；Kustomize 負責不同環境 Overlay；Argo CD 持續監控 Git Repository 並自動同步到 Kubernetes。

---

## Q2

為什麼最後把 Ingress Host 從 Kustomize Patch 改成 Helm Values？

因為 Ingress 的 `spec.rules` 屬於 List，Strategic Merge Patch 會直接取代整個 Rules，導致 `http.paths` 與 `backend` 消失。Host 屬於可參數化設定，使用 Helm Values 管理更符合 Helm 的設計，也避免 Patch 覆蓋問題。
