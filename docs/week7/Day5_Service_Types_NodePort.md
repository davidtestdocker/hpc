<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day5 — Service type 與 NodePort

[上一課](<Day4_Liveness_and_Readiness_Probe.md>) · [本週目錄](README.md) · [下一課](<Day6_Ingress_Traefik.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

ClusterIP 提供叢集內虛擬服務位址；NodePort 可透過節點埠暴露，但還受防火牆與路由限制。主展示可用顯式 context 的 port-forward，不依賴舊 node IP。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/templates/service.yaml](<../../helm/api/templates/service.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  type: {{ .Values.service.type }}

  # 選取要關聯的物件；不同資源種類支援的 selector 格式不同。
  selector:
    {{- include "api.selectorLabels" . | nindent 4 }}

  # 連接埠設定清單；容器宣告埠號本身不會自動對外公開。
  ports:
    - port: {{ .Values.service.port }}
      # Service 將流量轉送至 Pod 的目標埠號或命名埠。
      targetPort: {{ .Values.service.targetPort }}
      {{- if eq .Values.service.type "NodePort" }}
      # 經節點 IP 開放的 Service 埠號，適用 NodePort／部分 LoadBalancer 配置。
      nodePort: {{ .Values.service.nodePort }}
      {{- end }}
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day5_Service_Types_NodePort.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day5 - Service Types and NodePort

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-service.yaml](../../k8s/api-service.yaml)
- [loadtest/benchmark.js](../../loadtest/benchmark.js)：k6 API 壓測

---

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
