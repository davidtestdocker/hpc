# Week7 Day4 - Liveness Probe and Readiness Probe

## 今日平台增加什麼

今天平台新增 Kubernetes Health Check。

API Pod 開始具備：

* Readiness Probe
* Liveness Probe
* Self-healing

平台開始具備自動健康檢查與自我修復能力。

---

# Platform Problem

Pod 處於 Running 並不代表應用程式已經可以提供服務。

例如：

```text
FastAPI 啟動
        │
        ▼
Redis 尚未連線
        │
        ▼
Database 尚未初始化
```

若此時 Service 已開始轉送流量，就可能產生大量 500 Error。

此外，如果應用程式發生 Deadlock、Infinite Loop 或其他無法正常工作的情況，Container 可能仍維持 Running 狀態，但已無法提供服務。

因此 Kubernetes 提供兩種 Probe。

---

# 今日知識鏈

```text
Container
      │
      ├── Readiness Probe
      │         │
      │         ▼
      │    Service 是否送流量
      │
      └── Liveness Probe
                │
                ▼
        Kubernetes 是否重新啟動 Container
```

---

# Readiness Probe

用途：

判斷 Pod 是否已準備好接收流量。

本課程設定：

```yaml
readinessProbe:
  httpGet:
    path: /health/redis
    port: 8000

  initialDelaySeconds: 5
  periodSeconds: 10
```

說明：

* 啟動後等待 5 秒開始檢查
* 每 10 秒檢查一次
* 若檢查失敗，Pod 會被標記為 NotReady
* Service 不再將流量導向此 Pod

Readiness **不會重新啟動 Container**。

---

# Liveness Probe

用途：

判斷 Container 是否仍正常運作。

本課程設定：

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000

  initialDelaySeconds: 10
  periodSeconds: 10
```

若 Liveness 檢查失敗：

* Kubelet 終止 Container
* Deployment 自動重新建立 Container

這就是 Kubernetes Self-healing。

---

# Hands-on

## 新增 Readiness Probe

API Deployment：

```yaml
readinessProbe:
  httpGet:
    path: /health/redis
    port: 8000
```

驗證：

```bash
kubectl describe pod -n hpc-platform -l app=api
```

確認：

```text
Readiness:
http-get http://:8000/health/redis
```

---

## 新增 Liveness Probe

API Deployment：

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
```

驗證：

```bash
kubectl describe pod -n hpc-platform -l app=api
```

確認：

```text
Liveness:
http-get http://:8000/health
```

---

## Self-healing 實驗

故意修改：

```yaml
path: /health-xxxx
```

重新部署後觀察：

```bash
kubectl get pods -n hpc-platform -w
```

結果：

* Pod Restart
* RESTARTS 增加
* Events 顯示 Liveness probe failed

恢復正確 Path 後：

Pod 恢復正常。

---

# Readiness 與 Liveness 差異

| 項目               | Readiness       | Liveness          |
| ---------------- | --------------- | ----------------- |
| 目的               | 是否可以接流量         | 是否需要重啟            |
| 檢查失敗             | Pod 標記 NotReady | Container Restart |
| Service 是否送流量    | 否               | 否（Container 重啟期間） |
| 是否重新啟動 Container | 否               | 是                 |

---

# 今日重點

* Running 不代表 Ready。
* Readiness 控制流量。
* Liveness 控制自我修復。
* Kubernetes 可透過 Probe 自動維持服務健康。

---

# Interview Q&A

## Q1：Running 和 Ready 一樣嗎？

不一樣。

Running 表示 Container 已啟動。

Ready 表示 Pod 已通過 Readiness Probe，可以接收流量。

---

## Q2：Readiness 失敗會重啟 Pod 嗎？

不會。

Pod 只會退出 Service 的 Endpoints，不再接收流量。

---

## Q3：Liveness 失敗會發生什麼？

Kubelet 會終止 Container，Deployment 會重新建立並啟動新的 Container。

---

# 今日成果

API Pod 已具備：

```text
Deployment
      │
      ▼
Pod
      │
      ├── ConfigMap
      ├── Secret
      ├── Requests
      ├── Limits
      ├── Readiness Probe
      └── Liveness Probe
```

平台開始具備 Kubernetes 生產環境常見的 Health Check 與 Self-healing 能力。

---

# 下一步

Week7 Day5：

* Service Types
* ClusterIP
* NodePort
* LoadBalancer
* 為什麼 Ingress 一定建立在 Service 之上

