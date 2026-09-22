<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day2 — Pod、image 與 Secret 安全

[上一課](<day1-rbac-serviceaccount-least-privilege.md>) · [本週目錄](README.md) · [下一課](<day3-networkpolicy-tenant-isolation.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：歷史安全Pod與現存設定。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

完整securityContext與digest只在此測試Pod，不是全專案已套用；API Docker非root也不自動等於readonly/seccomp/dropALL。digest固定內容不保證無漏洞或可信來源。

## 程式／設定與來源

本次核對：[k8s/security/rbac-api-test.yaml](<../../k8s/security/rbac-api-test.yaml>)、[docker/Dockerfile](<../../docker/Dockerfile>)

## 已有結果與解讀

來源：[記錄／示例原文](<day2-pod-image-secret-security.md>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
94e9e444bcba979c2ea12e27ae39bee4cd10bc7041a472c4727a558e213744e6
```

保留歷史HTTP結果，無新漏洞掃描／credential rotation證據；不把從Git移除現檔說成歷史秘密已清除。

**仍缺的證據／不能證明的事：** 缺當時完整 raw log、精確日期或環境快照；本次只核對文件與程式，不重跑，也不把設定存在當成執行成功。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：已驗證 worker 重啟接續；不等於 node failover、Redis 全失恢復或跨 DB 原子交易。
> **閱讀順序**：先學本文基礎，再讀[Week20 現行對照與檢核](../learning-guide.md#week20)及[對應現行入口](../runbooks/automatic-worker.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week20 Day2 — Pod / Image / Secret Security

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置
- [k8s/postgres-secret.example.yaml](../../k8s/postgres-secret.example.yaml)
- [k8s/postgres-statefulset.yaml](../../k8s/postgres-statefulset.yaml)
- [k8s/security/rbac-api-test.yaml](../../k8s/security/rbac-api-test.yaml)
- [k8s/security/role.yaml](../../k8s/security/role.yaml)
- [k8s/security/rolebinding.yaml](../../k8s/security/rolebinding.yaml)
- [k8s/security/serviceaccount.yaml](../../k8s/security/serviceaccount.yaml)

---

## 今日完成

完成 workload runtime security、image integrity、secret hygiene。

---

## 1. RBAC vs Pod Security

RBAC：

    控制 Pod 可以對 Kubernetes API 做什麼

Pod Security：

    控制 container runtime 本身可以做什麼

兩者是不同安全層。

---

## 2. Pod Security Baseline

在 rbac-api-test 加入：

    seccompProfile:
      type: RuntimeDefault

Container：

    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000

    allowPrivilegeEscalation: false

    readOnlyRootFilesystem: true

    capabilities:
      drop:
        - ALL

---

## 3. runAsNonRoot

限制 container process：

    不使用 UID 0

本次：

    UID = 1000
    GID = 1000

降低 container 被入侵後取得 root runtime 權限的風險。

---

## 4. Privilege Escalation

設定：

    allowPrivilegeEscalation: false

避免 process 透過 setuid / setgid 等方式取得更高權限。

---

## 5. Linux Capabilities

設定：

    capabilities:
      drop:
        - ALL

代表移除 container 不需要的 Linux privileged capabilities。

原則：

    預設全部移除
    ↓
    真正需要時才 individually add

---

## 6. Read-Only Root Filesystem

設定：

    readOnlyRootFilesystem: true

代表 container image filesystem 不允許 runtime 修改。

程式需要寫：

    /tmp

因此另外使用：

    emptyDir
    ↓
    mount /tmp

形成：

    root filesystem → read-only
    必要 runtime path → writable

---

## 7. seccomp

使用：

    RuntimeDefault

seccomp 用來限制 Linux system calls。

目的：

    減少 container 可以呼叫的 kernel attack surface

---

## 8. Hardening 後功能驗證

實際 Pod：

    Completed

Security Context：

    RuntimeDefault                ✓
    runAsNonRoot=true             ✓
    runAsUser=1000                ✓
    allowPrivilegeEscalation=false ✓
    readOnlyRootFilesystem=true   ✓
    capabilities drop ALL         ✓

原本 RBAC 功能仍正常：

    GET Pods
    → HTTP 200

    GET Secrets
    → HTTP 403

    DELETE Pod
    → HTTP 403

代表：

    security hardening
    +
    workload functionality

可以同時成立。

---

## 9. Secret Security 問題

掃描 repo 發現：

    postgres-statefulset.yaml

曾直接包含：

    POSTGRES_PASSWORD
    value: <password>

以及：

    postgres-secret.yaml

把密碼以 Base64 放進 Git。

重要：

    Base64 ≠ Encryption

因此 Kubernetes Secret YAML 直接 commit 真值，
仍屬於 secret exposure。

---

## 10. secretKeyRef

StatefulSet 改成：

    POSTGRES_PASSWORD
    ↓
    valueFrom
    ↓
    secretKeyRef
    ↓
    postgres-secret

因此 workload manifest：

    知道 Secret name / key

但：

    不需要知道真正 password value

---

## 11. Secret 不進 Git

舊：

    postgres-secret.yaml
    → 真實 secret value
    → Git tracked

修正：

    postgres-secret.yaml
    → 移出 Git tracking
    → 加入 .gitignore

Repo 改留：

    postgres-secret.example.yaml

用途：

    描述需要哪些 Secret keys
    但不包含真正 credential。

---

## 12. Secret Rotation

如果 secret 曾進入 Git：

    刪掉目前檔案
    ≠
    從 Git history 消失

因此曾經 commit 的 credential：

    應視為已曝光

未來重新使用該服務時：

    必須換新 credential

不能繼續使用舊 password。

---

## 13. ServiceAccount Token

Repo 中：

    /var/run/secrets/kubernetes.io/serviceaccount/token

不是 credential 洩漏。

因為 repo 只記錄：

    token runtime path

真正 token：

    由 Kubernetes runtime 注入 Pod

---

## 14. Image Security

使用：

    image:tag

例如：

    curlimages/curl:8.12.1

比：

    :latest

安全，因為版本比較固定。

但 tag 仍可能被 registry 重新指向不同 image。

---

## 15. Image Digest Pinning

從實際執行成功的 Pod 取得：

    imageID

結果：

    curlimages/curl@sha256:94e9e444bcba979c2ea12e27ae39bee4cd10bc7041a472c4727a558e213744e6

Repo 改成：

    image@sha256:<digest>

好處：

    Deployment 指向 immutable image content

而不是只相信可變的 tag。

---

## 16. 最終 Security Model

    Source Code / Git
        ↓
    No plaintext secrets
        ↓
    Pinned image digest
        ↓
    Kubernetes Secret runtime injection
        ↓
    ServiceAccount identity
        ↓
    RBAC least privilege
        ↓
    Non-root container
        ↓
    No privilege escalation
        ↓
    Drop capabilities
        ↓
    Read-only root filesystem
        ↓
    RuntimeDefault seccomp

---

## 17. Repo

    k8s/security/
    ├─ serviceaccount.yaml
    ├─ role.yaml
    ├─ rolebinding.yaml
    └─ rbac-api-test.yaml

另外：

    k8s/postgres-statefulset.yaml
    → secretKeyRef

    k8s/postgres-secret.example.yaml
    → safe Secret template

    .gitignore
    → ignore real postgres-secret.yaml

---

## Interview Review

**Q1：Kubernetes Secret 使用 Base64 後，是否適合直接 commit 到 Git？**  
A：不適合。Base64 只是編碼，不是加密。真正的 secret value 不應直接進 Git，workload manifest 應透過 secretKeyRef 或 external secret manager 在 runtime 取得。

**Q2：為什麼 production container 常設定 non-root、drop capabilities、readOnlyRootFilesystem 和 seccomp？**  
A：目的是降低 container 被入侵後可利用的權限與 kernel attack surface，限制 privilege escalation、filesystem modification 與不必要的 Linux capabilities。
