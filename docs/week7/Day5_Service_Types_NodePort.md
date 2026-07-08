# Week7 Day5 - Service Types and NodePort

## 今日平台增加什麼

今天平台完成 Kubernetes Service Type 的學習。

API Service 從：

```text
ClusterIP
```

修改為：

```text
NodePort
```

並成功透過 Node IP 對外提供服務。

---

# Platform Problem

前幾天測試 API 時，我們一直使用：

```bash
kubectl port-forward -n hpc-platform svc/api-service 8000:8000
```

雖然可以正常測試：

```text
localhost:8000
```

但：

這只是 Kubernetes 建立的一條臨時 Tunnel。

真正的 Service 並沒有直接對外提供服務。

---

# 今日知識鏈

```text
Internet
    │
Node IP
    │
NodePort
    │
ClusterIP Service
    │
Pod
```

理解 Kubernetes 對外流量的第一步。

---

# Kubernetes Service Types

## ClusterIP

預設 Service Type。

只能提供 Cluster 內部存取。

例如：

```text
api Pod
    │
redis-service
    │
redis Pod
```

Pod 與 Pod 之間透過 Service Name 通訊。

---

## NodePort

NodePort 會在每個 Node 開啟固定 Port。

例如：

```text
Node IP
10.140.0.2

↓

30080

↓

api-service

↓

api Pod
```

外部即可透過：

```text
http://10.140.0.2:30080
```

存取 API。

---

## LoadBalancer

在雲端平台（例如 GKE、EKS、AKS）：

```yaml
type: LoadBalancer
```

Kubernetes 會自動向 Cloud Provider 建立真正的 Load Balancer。

通常會取得：

```text
Public IP
```

供 Internet 存取。

---

# Hands-on

修改：

```text
k8s/api-service.yaml
```

內容：

```yaml
apiVersion: v1
kind: Service

metadata:
  name: api-service
  namespace: hpc-platform

spec:
  type: NodePort

  selector:
    app: api

  ports:
    - port: 8000
      targetPort: 8000
      nodePort: 30080
```

部署：

```bash
kubectl apply -f k8s/api-service.yaml
```

---

# 驗證 Service

查看：

```bash
kubectl get svc -n hpc-platform
```

結果：

```text
api-service

TYPE: NodePort

PORT:
8000:30080/TCP
```

代表 NodePort 建立成功。

---

# 驗證 API

取得 Node IP：

```bash
kubectl get nodes -o wide
```

Node：

```text
10.140.0.2
```

測試：

```bash
curl http://10.140.0.2:30080/health/redis
```

以及：

```bash
curl http://localhost:30080/health/redis
```

結果：

```json
{
  "status": "healthy",
  "redis": "connected"
}
```

代表：

NodePort → Service → Pod

完整打通。

---

# Port-forward 與 NodePort 差異

## Port-forward

```text
kubectl port-forward
        │
        ▼
ClusterIP
        │
        ▼
Pod
```

用途：

* 本機開發
* Debug
* 臨時測試

不屬於正式對外服務方式。

---

## NodePort

```text
Client
    │
NodeIP:30080
    │
NodePort
    │
ClusterIP
    │
Pod
```

用途：

* Lab
* Home Lab
* Bare Metal
* 沒有 Cloud LoadBalancer 的環境

---

# 為什麼企業很少直接使用 NodePort？

假設平台包含：

* API
* Grafana
* Prometheus
* Argo CD

若全部使用 NodePort：

```text
30080
30081
30082
30083
```

使用者必須記住大量 Port。

因此企業通常改用：

```text
Internet
     │
Ingress
     │
ClusterIP Service
     │
Pod
```

透過同一個 80 / 443 Port，依照 Host 或 Path 將流量導向不同 Service。

---

# 平台架構

```text
Client
    │
10.140.0.2:30080
    │
NodePort
    │
api-service
    │
api Pod
    │
Redis
```

---

# 今日重點

* ClusterIP 只能在 Cluster 內使用。
* Port-forward 是 Kubernetes 提供的除錯工具。
* NodePort 可直接透過 Node IP 對外提供服務。
* NodePort 建立於 ClusterIP 之上。
* Ingress 建立於 Service 之上，而不是直接連 Pod。

---

# Interview Q&A

## Q1：Port-forward 和 NodePort 差在哪？

Port-forward 建立一條臨時 Tunnel，主要用於開發與除錯。

NodePort 則是在每個 Node 開啟固定 Port，提供外部存取。

---

## Q2：NodePort 和 ClusterIP 是互斥的嗎？

不是。

NodePort Service 底層仍然會建立 ClusterIP。

流量流程：

```text
NodePort
    │
ClusterIP
    │
Pod
```

---

## Q3：為什麼企業通常不用大量 NodePort？

因為管理困難。

正式環境通常使用：

* LoadBalancer
* Ingress

讓多個 Service 共用 80 / 443 Port。

---

# 今日成果

平台正式具備 Kubernetes 對外存取能力：

```text
Client
    │
NodePort
    │
ClusterIP Service
    │
API Pod
```

完成：

* Service Types
* NodePort
* 對外存取
* Service 流量模型

---

# 下一步

Week7 Day6：

Traefik Ingress。

學習：

* Ingress Resource
* Host Routing
* Path Routing
* Traefik Controller
* 為什麼正式環境幾乎都使用 Ingress 作為唯一入口。

