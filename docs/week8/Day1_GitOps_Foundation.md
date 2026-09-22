<!-- readable-curriculum: 2026-09-22 -->
# Week8 Day1 — GitOps 的期望狀態

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2_Helm_Foundation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

GitOps 不只是把 YAML 放進 Git，還需要控制器讀取指定 revision 並協調叢集。主環境目前不是既有 dev Application 的完整受管目標；配置存在也不是同步成功證據。

## 在現在的專案中

主線是 Helm／Kustomize 渲染與 deploy 工具；Argo CD 為獨立 GitOps 設定教材。

本課對照：[argocd/application-dev.yaml](<../../argocd/application-dev.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  source:
    repoURL: https://github.com/davidtestdocker/hpc.git
    targetRevision: master
    # 歷史 dev 路徑，不是現行 gpu-sg-platform。切換前須檢查 diff／資源所有權；
    # 下方 prune=true 可能刪除舊受管資源，不可把改路徑當成單純文件同步。
    path: kustomize/overlays/dev

  # Argo CD 同步目標叢集與 namespace。
  destination:
    #Kubernetes API Server 的DNS，意思部屬到目前這個Cluster
    server: https://kubernetes.default.svc
    namespace: hpc-platform-dev

  # Argo CD 自動同步與資源管理政策。
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
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week8/Day1_GitOps_Foundation.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 overlay 是 gpu-sg-platform；Argo dev 仍指 overlays/dev，不能宣稱主環境已完成 GitOps 對齊。
> **閱讀順序**：先學本文基礎，再讀[Week8 現行對照與檢核](../learning-guide.md#week8)及[對應現行入口](../../kustomize/overlays/gpu-sg-platform/kustomization.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week8 Day1 - GitOps Foundation

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [argocd/application-dev.yaml](../../argocd/application-dev.yaml)
- [argocd/project.yaml](../../argocd/project.yaml)
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)
- [k8s/api-ingress.yaml](../../k8s/api-ingress.yaml)
- [k8s/api-service.yaml](../../k8s/api-service.yaml)

---

## 本週成果

建立 Production Deployment Pipeline。

平台將從：

```text
手動 kubectl apply
```

進化為：

```text
Git

↓

Argo CD

↓

Kubernetes
```

開始建立企業級 GitOps 部署流程。

---

# 今日平台增加什麼

今天建立 GitOps 核心概念。

新增：

```text
gitops/
```

目錄，作為後續 GitOps 相關檔案與部署流程的起點。

目前專案：

```text
hpc-ai-benchmark-platform/

├── api/
├── benchmark/
├── docs/
├── k8s/
├── monitoring/
├── loadtest/
└── gitops/
```

---

# Platform Problem

目前平台部署方式：

```bash
kubectl apply -f api-deployment.yaml

kubectl apply -f api-service.yaml

kubectl apply -f api-ingress.yaml
```

這種方式稱為：

```text
Imperative Deployment
```

雖然簡單，但存在許多問題：

* 不知道誰修改了設定
* Deployment 歷史難以追蹤
* Cluster 容易與 Git 不一致
* 無法自動修正 Drift

---

# GitOps 是什麼？

GitOps 的核心理念：

> **Git 是唯一事實來源（Single Source of Truth）。**

所有 Kubernetes 設定都以 Git Repository 為準。

任何部署都必須先修改 Git，再同步到 Cluster。

---

# 傳統部署流程

```text
Engineer
     │
kubectl apply
     │
Kubernetes Cluster
```

工程師直接操作 Cluster。

---

# GitOps 部署流程

```text
Engineer
     │
git commit
     │
git push
     │
Git Repository
     │
Argo CD
     │
Kubernetes Cluster
```

工程師不直接修改 Cluster。

所有修改都經過 Git。

---

# Desired State

Git Repository：

```yaml
replicas: 2
```

代表：

平台應該有：

```text
2 Pods
```

這就是：

```text
Desired State
```

---

# Actual State

目前 Cluster：

```text
5 Pods
```

代表：

Cluster 與 Git 已經不同。

這就是：

```text
Configuration Drift
```

---

# Reconciliation

Argo CD 持續比較：

```text
Desired State
```

與：

```text
Actual State
```

如果不同：

```text
Git

2 Pods

↓

Cluster

5 Pods

↓

Argo CD

↓

Scale 回 2 Pods
```

這個持續同步的過程稱為：

```text
Reconciliation
```

---

# Self Heal

若有人直接執行：

```bash
kubectl scale deployment api --replicas=10
```

Git：

```text
replicas = 2
```

Argo CD 偵測到 Drift 後：

```text
10 Pods

↓

2 Pods
```

自動恢復到 Git 定義的狀態。

這就是：

```text
Self Heal
```

---

# GitOps 架構

```text
Git Repository
        │
Desired State
        │
Argo CD
        │
Reconciliation
        │
Kubernetes Cluster
        │
Actual State
```

---

# Hands-on

建立：

```text
gitops/
```

指令：

```bash
mkdir gitops
```

確認：

```bash
tree -L 1
```

專案結構已新增：

```text
gitops/
```

---

# 今日重點

* GitOps 以 Git 作為唯一事實來源。
* 不直接修改 Kubernetes Cluster。
* Desired State 定義於 Git。
* Actual State 為 Cluster 現況。
* Argo CD 持續進行 Reconciliation。
* Self Heal 可自動修正 Configuration Drift。

---

# Interview Q&A

## Q1：什麼是 GitOps？

GitOps 是以 Git Repository 作為 Kubernetes 唯一設定來源，由 Git 控制部署與變更。

---

## Q2：什麼是 Desired State？

Desired State 是 Git Repository 中定義的平台狀態，例如 Deployment、Service、Ingress、Replica 數量等。

---

## Q3：什麼是 Reconciliation？

Reconciliation 是 GitOps Controller（例如 Argo CD）持續比較 Desired State 與 Actual State，並自動同步兩者的過程。

---

# 今日成果

平台開始從傳統部署方式：

```text
Engineer

↓

kubectl apply
```

邁向企業級 GitOps：

```text
Engineer

↓

Git Commit

↓

Git Push

↓

Argo CD

↓

Kubernetes
```

建立 GitOps 思維，為後續 Helm、Kustomize、Argo CD 做準備。

---

# 下一步

Week8 Day2：

Helm Foundation

學習：

* Helm Chart
* Chart.yaml
* values.yaml
* templates
* Helm Template Render
* 建立第一個 Helm Chart
