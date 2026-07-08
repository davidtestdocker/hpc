# Week7 Day6 - Ingress and Traefik

## 今日平台增加什麼

今天平台完成 Kubernetes Ingress。

使用 K3s 內建 Traefik 作為 Ingress Controller，讓 API 可以透過 HTTP 網址存取，而不是直接使用 NodePort。

平台正式建立：

* Traefik Ingress Controller
* Ingress Resource
* Path Routing
* Host Routing

---

# Platform Problem

前一天平台使用：

```text
NodeIP:30080
```

例如：

```text
http://10.140.0.2:30080
```

雖然可以正常提供服務，但如果平台增加：

* API
* Grafana
* Prometheus
* Argo CD

就會變成：

```text
30080
30081
30082
30083
```

需要記住大量 Port。

正式環境通常不會這樣設計。

---

# 今日知識鏈

```text
Client
    │
DNS
    │
api.hpc.local
    │
Traefik
    │
Ingress
    │
ClusterIP Service
    │
API Pod
```

Ingress 專門負責 HTTP / HTTPS 的流量轉送。

---

# Traefik Ingress Controller

K3s 安裝完成後，已自動部署：

```bash
kubectl get svc -n kube-system
```

結果：

```text
traefik

TYPE:
LoadBalancer

EXTERNAL-IP:
10.140.0.2

PORTS:
80
443
```

Traefik 負責接收所有 HTTP / HTTPS 流量。

---

# Ingress Resource

建立：

```text
k8s/api-ingress.yaml
```

內容：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: api-ingress
  namespace: hpc-platform

spec:
  rules:
    - host: api.hpc.local

      http:

        paths:

          - path: /

            pathType: Prefix

            backend:

              service:

                name: api-service

                port:

                  number: 8000
```

部署：

```bash
kubectl apply -f k8s/api-ingress.yaml
```

---

# Path Routing

最初測試：

```text
/health

/benchmark
```

分別導向：

```text
api-service
```

最後修改為：

```text
path: /
```

代表：

所有 API：

```text
/

↓

api-service
```

因此：

```text
/health

/health/redis

/jobs

/docs

/openapi.json
```

全部都交給 FastAPI。

這也是企業最常見的設定。

---

# Host Routing

新增：

```yaml
host:
api.hpc.local
```

代表：

只有：

```text
api.hpc.local
```

才符合此規則。

本機：

修改：

```text
/etc/hosts
```

加入：

```text
10.140.0.2 api.hpc.local
```

即可模擬正式 DNS。

---

# 驗證

測試：

```bash
curl http://api.hpc.local/health
```

結果：

```json
{
  "status": "healthy"
}
```

另外驗證：

```bash
curl http://10.140.0.2/health
curl http://10.140.0.2/health/redis
curl http://10.140.0.2/jobs
curl http://10.140.0.2/docs
```

全部成功。

代表：

Traefik

↓

Ingress

↓

Service

↓

Pod

完整打通。

---

# Ingress 與 NodePort 差異

## NodePort

```text
Client
    │
NodeIP:30080
    │
Service
    │
Pod
```

需要知道：

* Node IP
* Port

---

## Ingress

```text
Client
    │
api.hpc.local
    │
Traefik
    │
Ingress
    │
Service
    │
Pod
```

使用 Domain Name，而不是記住 Port。

---

# 為什麼企業偏好 Ingress？

正式環境通常包含多個服務：

```text
api.company.com
grafana.company.com
argocd.company.com
prometheus.company.com
```

全部共用：

```text
80
443
```

Ingress 根據：

* Host
* Path

將流量導向不同 Service。

---

# 平台架構

```text
Client
    │
api.hpc.local
    │
Traefik (Ingress Controller)
    │
Ingress
    │
api-service
    │
API Pod
    │
Redis
    │
PostgreSQL
```

---

# 今日重點

* Ingress 建立於 Service 之上。
* Traefik 是 Ingress Controller。
* Path Routing 可依 URL 路徑轉送流量。
* Host Routing 可依 Domain Name 轉送流量。
* 正式環境通常使用 Ingress，而不是大量 NodePort。

---

# Interview Q&A

## Q1：Ingress 可以直接連 Pod 嗎？

不能。

Ingress 一律導向 Service，再由 Service 導向 Pod。

---

## Q2：Traefik 和 Ingress 是同一個東西嗎？

不是。

Traefik 是 Ingress Controller。

Ingress 是 Kubernetes Resource，描述流量規則。

Traefik 會讀取 Ingress 規則並實際轉送流量。

---

## Q3：為什麼企業偏好 Host Routing？

因為不同服務可共用 80 / 443 Port。

例如：

* api.company.com
* grafana.company.com
* argocd.company.com

不需要記住不同的 NodePort。

---

# 今日成果

平台正式完成 HTTP 流量入口：

```text
Client
    │
DNS
    │
Traefik
    │
Ingress
    │
ClusterIP Service
    │
API Pod
```

這是 Kubernetes 生產環境最典型的 HTTP 流量架構。

---

# 下一步

Week7 Day7：

Horizontal Pod Autoscaler（HPA）

使用 metrics-server 與 k6 壓力測試，讓 API Pod 根據 CPU 使用率自動擴容。

