<!-- readable-curriculum: 2026-09-22 -->
# Week20 Day2 — Pod、image 與 Secret 安全

[上一課](<day1-rbac-serviceaccount-least-privilege.md>) · [本週目錄](README.md) · [下一課](<day3-networkpolicy-tenant-isolation.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

image digest 用於追溯內容，securityContext 限制執行權限，Secret mount 提供憑證。任何單一設定都不等於全面 hardening，init container 改權限也需看實際需要。

## 在現在的專案中

保留所有歷史成功與失敗；不宣稱 node failover、Redis 全失恢復或跨資料庫原子交易。

本課對照：[api/workloads/templates/jobset-mpi.yaml](<../../api/workloads/templates/jobset-mpi.yaml>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```yaml
              initContainers:
                - name: prepare-ssh
                  # 容器映像及標籤，決定執行的檔案系統與程式版本。
                  image: mpioperator/mpi-pi:openmpi
                  # 程序身分、權限與作業系統安全設定。
                  securityContext:
                    runAsUser: 0
                  # 覆寫容器入口指令；多行字串中的 Shell 語法由指定的 shell 解讀。
                  command:
                    - /bin/sh
                    - -lc
                    - |
                      set -e
                      cp /ssh-secret/id_ed25519 /ssh-work/id_ed25519
                      chown 1000:1000 /ssh-work/id_ed25519
                      chmod 600 /ssh-work/id_ed25519
                  # 把已宣告的 volume 掛載到容器中的指定路徑。
                  volumeMounts:
                    - name: ssh-secret
                      # 容器內可見的掛載路徑。
                      mountPath: /ssh-secret
                      # 是否以唯讀方式掛載，限制容器透過此掛載點寫入。
                      readOnly: true
                    - name: ssh-work
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week20/day2-pod-image-secret-security.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

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
