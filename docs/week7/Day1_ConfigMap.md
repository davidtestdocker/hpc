# Week7 Day1 - ConfigMap

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

