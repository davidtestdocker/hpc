<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day1 — ConfigMap 與環境變數

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2_Secret.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

ConfigMap 不應放密碼。主 chart 提供 Redis／DB 連線設定及 AUTOMATIC_WORKER，後者也影響手動端點能否使用；它不是 GPU 是否存在的旗標。

## 在現在的專案中

學習現行 chart；歷史 Traefik／NodePort 位址不當作可用入口。

本課對照：[helm/api/templates/configmap.yaml](<../../helm/api/templates/configmap.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
  AUTOMATIC_WORKER: {{ .Values.worker.enabled | quote }}
  WORKER_POLL_SECONDS: {{ .Values.worker.pollSeconds | quote }}
  REDIS_HOST: {{ .Values.config.redisHost | quote }}
  REDIS_PORT: {{ .Values.config.redisPort | quote }}
  POSTGRES_HOST: {{ .Values.config.postgresHost | quote }}
  POSTGRES_PORT: {{ .Values.config.postgresPort | quote }}
  POSTGRES_DB: {{ .Values.config.postgresDb | quote }}
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

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week7/Day1_ConfigMap.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：現行 API 與 worker 分開部署；API HPA 不等於 worker 擴縮，Secret 不應保存真實密碼。
> **閱讀順序**：先學本文基礎，再讀[Week7 現行對照與檢核](../learning-guide.md#week7)及[對應現行入口](../../helm/api/templates/worker.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week7 Day1 - ConfigMap

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [k8s/api-configmap.yaml](../../k8s/api-configmap.yaml)
- [k8s/api-deployment.yaml](../../k8s/api-deployment.yaml)

---

## 今日平台增加什麼

今天平台新增：

```text
ConfigMap
```

把原本寫死在 Deployment 裡的非敏感設定抽出來。

---

# Platform Problem

原本 API Deployment 直接寫：

```text
REDIS_HOST
REDIS_PORT
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
```

這會造成：

* Deployment YAML 變難維護
* Stage / Prod 環境難切換
* 設定和應用程式部署邏輯混在一起

---

# 今日知識鏈

```text
Hard-coded env
    ↓
ConfigMap
    ↓
Pod Environment
```

---

# Hands-on

建立：

```text
k8s/api-configmap.yaml
```

內容包含：

```text
REDIS_HOST
REDIS_PORT
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
```

套用：

```bash
kubectl apply -f k8s/api-configmap.yaml
```

修改 API Deployment：

```yaml
envFrom:
  - configMapRef:
      name: api-config
```

---

# 驗證

查看 ConfigMap：

```bash
kubectl get configmap -n hpc-platform
kubectl describe configmap api-config -n hpc-platform
```

查看 Pod Environment 來源：

```bash
kubectl describe pod -n hpc-platform -l app=api | grep -A20 "Environment"
```

確認：

```text
Environment Variables from:
  api-config  ConfigMap  Optional: false
```

---

# 平台架構

```text
api-config ConfigMap
        ↓
api Deployment
        ↓
api Pod Environment
```

---

# 今日重點

* ConfigMap 用來保存非敏感設定。
* Deployment 不應硬寫環境設定。
* ConfigMap 適合保存 Host、Port、Database Name 等資訊。
* Password、Token、API Key 不應放 ConfigMap。

---

# Interview Q&A

## Q1：ConfigMap 解決什麼問題？

ConfigMap 將非敏感設定從 Deployment 中抽離，讓 Application 與 Configuration 分離，方便多環境管理。

## Q2：ConfigMap 可以放密碼嗎？

不建議。密碼、Token、API Key 應該放 Secret。

---

# 下一步

Week7 Day2：

使用 Secret 管理 PostgreSQL 密碼與敏感資訊。
