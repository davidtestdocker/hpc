<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day6 — Ingress 與 Controller

[上一課](<Day5_Service_Types_NodePort.md>) · [本週目錄](README.md) · [下一課](<Day7_Horizontal_Pod_Autoscaler.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

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

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day6_Ingress_Traefik.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day6 - Ingress and Traefik

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-ingress.yaml](../../k8s/api-ingress.yaml)

---

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
