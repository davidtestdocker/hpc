# Week20 Day2 — Pod / Image / Secret Security

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
