<!-- readable-curriculum: 2026-09-22 -->
# Week7 Day1 — ConfigMap 與環境變數

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<Day2_Secret.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史 describe 摘錄。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

envFrom 的 ConfigMap 內容在建立容器時注入，改 ConfigMap 不表示既有程序的環境立即更新；現行模板沒有設定變更 checksum rollout。需區分設定引用與應用實際讀到值。

## 程式／設定與來源

本次核對：[k8s/api-deployment.yaml](<../../k8s/api-deployment.yaml>)、[k8s/api-configmap.yaml](<../../k8s/api-configmap.yaml>)、[helm/api/templates/configmap.yaml](<../../helm/api/templates/configmap.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<Day1_ConfigMap.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
api-config  ConfigMap  Optional: false
```

此行是舊 describe 文字，只證明當時記載引用來源，未保存各欄位值與連線驗收。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

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
