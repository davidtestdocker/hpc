<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day4 — Liveness 與 readiness

[上一課](<Day3_Resource_Requests_Limits_QoS.md>) · [本週目錄](README.md) · [下一課](<Day5_Service_Types_NodePort.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

readiness 失敗會影響 Service 流量，liveness 失敗可能重啟容器；主 API /health 只回程序訊號，不能稱為完整相依檢查。外部 DB 慢不一定適合用重啟 API 解決。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/templates/deployment.yaml](<../../helm/api/templates/deployment.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
        readinessProbe:
{{- toYaml .Values.readinessProbe | nindent 10 }}
        # 存活探針失敗達門檻時，kubelet 會重啟容器。
        livenessProbe:
{{- toYaml .Values.livenessProbe | nindent 10 }}
```

## 已有結果與解讀

### CPU 叢集重建：已保存的驗收結果

日期：2026-09-21。環境：隔離 CPU-only GKE 重建驗收；不是主環境的多 GPU 實驗。該次叢集已清理，讀這份結果不需要重新建立。

```json
{
  "recorded_at": "2026-09-21",
  "scope": "fresh CPU-only GKE bootstrap and platform acceptance; excludes GPU and MPI execution",
  "result": "pass",
  "terraform": {
    "apply": "3 added",
    "post_apply_plan": "No changes",
    "destroy": "3 destroyed",
    "state_resources_after_destroy": 0,
    "cluster_lookup_after_destroy": "404 Not Found"
  },
  "controllers": {
    "jobset": "v0.12.0 Ready on system-pool with 100m CPU request",
    "kueue": "v0.19.2 Ready on system-pool with Recreate deployment strategy"
  },
  "platform": {
    "api": "Running on system-pool; /health healthy",
    "redis": "Running on system-pool; connected; PVC Bound",
    "postgres": "Running on system-pool; jobs table query succeeded; PVC Bound",
    "overlay_diff_after_apply": "empty"
  },
  "security": {
    "postgres_secret": "created from external env file; value not captured",
    "mpi_ssh_key": "generated in temporary directory; value not captured",
    "api_service_account_create_jobsets": "yes",
    "api_service_account_delete_pods": "no"
  },
  "limitations": [
    "gpu-pool had zero nodes because project-wide GPU quota was exhausted",
    "no MPI workload was submitted in this CPU-only rehearsal",
    "database initialization used create_all rather than schema migration"
  ]
}
```

解讀：Terraform 建立 3 個資源、無 drift，JobSet／Kueue controllers 和 API／Redis／DB 驗收成功；create JobSet 權限允許，delete Pod 權限拒絕。最後 destroy 3、state 空、cluster 查詢 404，證明當次隔離叢集已刪除。**不包含 GPU 或 MPI 執行驗收**，也不是所有雲端資源的停費證明。

來源：[原始 CPU bootstrap JSON](<../evidence/cpu-bootstrap-acceptance-20260921.json>)。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day4_Liveness_and_Readiness_Probe.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day4 - Liveness Probe and Readiness Probe

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [api/main.py](../../api/main.py)：API、工作狀態與佇列處理
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)

---

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
