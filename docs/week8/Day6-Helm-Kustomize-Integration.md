# Week8 Day6 - Helm + Kustomize Integration

## 學習目標

完成 Helm 與 Kustomize 整合，建立可支援 Dev / Stage / Prod 的多環境部署流程。

---

# 完成成果

✅ API Helm Chart

✅ Redis Helm Chart

✅ PostgreSQL Helm Chart

✅ Kustomize Dev / Stage / Prod Overlay

✅ Helm + Kustomize Integration

✅ Dev 環境成功部署

---

# 專案架構

```
helm/
├── api/
├── redis/
└── postgres/

kustomize/
└── overlays/
    ├── dev/
    ├── stage/
    └── prod/
```

---

# 部署流程

```
Developer
      │
      ▼
kustomize/overlays/dev
      │
      ▼
Helm Render
      │
      ├── api
      ├── redis
      └── postgres
      │
      ▼
Kustomize Patch
      │
      ▼
kubectl apply
      │
      ▼
Kubernetes
```

---

# Helm 實際讀取順序

```
Chart.yaml
      ↓
values.yaml
      ↓
values-dev.yaml
      ↓
templates/*
      ↓
Render YAML
```

---

# Kustomize 做什麼？

Overlay 不建立 Resource。

Overlay 只負責：

- 選擇 Helm Chart
- 指定 Namespace
- 套用 Patch
- 套用不同環境設定

例如：

- replicas
- APP_ENV
- host

---

# Chart 職責

## API

- Deployment
- Service
- ConfigMap
- HPA
- Ingress

## Redis

- Deployment
- Service

## PostgreSQL

- StatefulSet
- Service
- Secret
- PVC

---

# 部署指令

```bash
kubectl kustomize kustomize/overlays/dev \
  --enable-helm \
  --load-restrictor LoadRestrictionsNone \
| kubectl apply -f -
```

---

# 今天踩到的重要坑

### 1. Helm Template 不要寫死 Namespace

❌

```yaml
namespace: hpc-platform
```

✅

```yaml
namespace: {{ .Release.Namespace }}
```

---

### 2. Patch 必須匹配正確 Namespace

否則：

```
no resource matches strategic merge patch
```

---

### 3. Secret 不要重複建立

PostgreSQL Chart：

建立 Secret

API Chart：

只引用 Secret

---

### 4. Dev 不使用 NodePort

避免：

```
provided port is already allocated
```

Dev 使用：

```
ClusterIP
```

---

### 5. imagePullPolicy: Never

代表：

Kubernetes 不會下載 Image。

新的 Image Tag 必須：

```
docker tag

↓

docker save

↓

k3s ctr images import
```

否則：

```
ErrImageNeverPull
```

---

### 6. replicaCount 不等於最終 Pod 數

```
Deployment replicas

↓

HPA

↓

依 CPU 自動 Scale
```

Deployment 的 replicas 只是初始值。

---

# Day6 完成後架構

```
Developer
      │
      ▼
Kustomize
      │
      ▼
Helm
      │
      ▼
Render YAML
      │
      ▼
Kubernetes
```

---

# Interview Q&A

## Q1：Helm 與 Kustomize 的角色差異？

**A：**

Helm 負責產生（Render）YAML。

Kustomize 負責依照不同環境修改 Render 後的 YAML。

---

## Q2：為什麼要拆成 api、redis、postgres 三個 Chart？

**A：**

因為每個服務可以獨立維護、升級、重複使用，符合企業實務。

---

## Q3：為什麼 Helm Template 不應寫死 Namespace？

**A：**

同一個 Chart 要能部署到 dev、stage、prod，不應綁定單一 Namespace。

---

## Q4：Deployment 的 replicas 為什麼最後會變？

**A：**

Deployment 的 replicas 是初始值，HPA 會依 CPU 使用率動態調整 Pod 數量。

---

## Q5：為什麼 Dev 使用 ClusterIP，而不是 NodePort？

**A：**

Dev 已經透過 Ingress 對外提供服務，使用 ClusterIP 可避免 NodePort 衝突並更符合實務部署方式。
