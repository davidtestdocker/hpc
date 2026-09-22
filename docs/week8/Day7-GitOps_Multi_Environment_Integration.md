<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day7 — 多環境與 Argo 邊界

[上一課](<Day6-Helm-Kustomize-Integration.md>) · [本週目錄](README.md) · [下一週](../week9/README.md) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：Expected 回覆，非現行部署證據。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

Expected 區塊不能當 raw evidence。三 namespace 不等於網路／故障域完全隔離；AppProject wildcard 資源規則也不是最小權限。現行 API 根路由固定 HPC API DEV，不能期待只靠環境 namespace 就回 STAGE/PROD。主 overlay 與 Argo dev 不同，未驗證自動 GitOps 主線。

## 程式／設定與來源

本次核對：[argocd/application-dev.yaml](<../../argocd/application-dev.yaml>)、[argocd/project.yaml](<../../argocd/project.yaml>)、[kustomize/overlays/gpu-sg-platform/kustomization.yaml](<../../kustomize/overlays/gpu-sg-platform/kustomization.yaml>)、[api/main.py](<../../api/main.py>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day7-GitOps_Multi_Environment_Integration.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
Synced

Healthy
```

保留原文 host／回應作歷史示例；未保存三個 Application 的完整 status/revision，不拿圖示勾選當現行驗收。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
