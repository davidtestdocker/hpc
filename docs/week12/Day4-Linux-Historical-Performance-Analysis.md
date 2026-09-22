<!-- readable-curriculum: 2026-09-22 -->
# Week12 Day4 — 歷史監控與時間對齊

[上一課](<Day3-Linux-Disk-Performance-Analysis.md>) · [本週目錄](README.md) · [下一課](<Day5-Linux-CPU-Benchmark-with-sysbench.md>) · [全程導讀](../learning-guide.md)

版本：2026-09-22。本文是現行版教材，按儲存庫實作解說；不是新一次雲端實測報告。

## 閱讀方式：不用再開 VM 或做本機測試

先看現行補充與已有結果，再往下讀完整原教材。原本的詳細說明、程式、命令與輸出都保留在本頁，不需要跳去文字快照，也不要求你重新驗證。

## 概念解說

單次 snapshot 無法描述整段事件；要對齊工作開始／結束、時區、取樣頻率與重啟時間。歷史資料可以證明當時觀察，不代表現在仍有同樣瓶頸。

## 在現在的專案中

歷史 Linux baseline 不是現行 MPI job 的自動 profiling；新硬體需重新建立基線。

本課對照：[docs/evidence/README.md](<../evidence/README.md>)。先看下面片段在檔案中的位置，再回到完整內容追輸入、處理與輸出。片段刻意只擷取相關起點，不可單獨貼去執行或 apply。

```text
| Linux Performance | [CPU analysis](../history/20260922-before-current/week12/Day1-Linux-CPU-Performance-Analysis.md)、[perf](../history/20260922-before-current/week12/Day6-Linux-CPU-Profiling-with-perf.md)、[strace](../history/20260922-before-current/week12/Day7-Linux-System-Call-Analysis-with-strace.md)、[CPU report](../../benchmark/cpu/results/cpu_benchmark_20260810.md) | Linux CPU／process／system-call 診斷紀錄與 stress-ng CPU saturation baseline | 歷史環境的輸出／報告；不是主 MPI job 的自動 profiling 或跨機型可直接比較的結果 |
| RBAC / Security | [API JobSet RBAC](../../k8s/security/api-jobset-rbac.yaml)、[RBAC 驗證](../history/20260922-before-current/week20/day1-rbac-serviceaccount-least-privilege.md)、[Pod hardening](../history/20260922-before-current/week20/day2-pod-image-secret-security.md)、[NetworkPolicy 實測](network-policy-validation-20260921.json) | API namespace-scoped JobSet 權限設定；歷史 benchmark-runner 允許／拒絕；隔離 Calico GKE ingress baseline／allow／deny／recovery | benchmark-runner 與 api-jobset-runner 是不同身份；NetworkPolicy 實測不在主 cluster，未涵蓋 egress、跨 namespace 或全平台 hardening |
| Terraform / GitOps | [Terraform 證據](terraform-gpu-sg-20260921.md)、[CPU-only bootstrap 驗收](cpu-bootstrap-acceptance-20260921.json)、[gpu-sg root](../../terraform/environments/gpu-sg/main.tf)、[歷史 GitOps 紀錄](../history/20260922-before-current/week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md) | 主環境 import 零 drift；全新 CPU-only cluster 完成 controllers／Secrets／queues／平台 bootstrap、health／RBAC／PVC 驗收及銷毀 | 不涵蓋全新 GPU cluster MPI 執行；缺 remote state；Argo dev 仍指舊 overlays/dev |
| L4 Causal LM / CUDA Profiling | [9/22 報告](../performance/causal-lm-l4-20260922.md)、[原始證據與 hashes](../../benchmark/results/causal-lm-20260922/evidence.json) | 13M causal LM、文字 byte tokens、交錯三次量測、兩份 CUDA traces、同步 nvidia-smi 遙測 | 單 L4 time-sharing；非 pretrained LLM 品質或多 GPU 結論；獨立 runner 尚未接 MPI API |

## Capability Matrix

狀態是證據標記，可同時存在，不是成熟度分數：

- **Implemented**：repo 有對應程式、script 或 declarative manifest；以「範圍」欄為準。
- **Validated**：repo 保存範圍內的執行或觀察結果；本索引使用既有 evidence，未重新執行實驗。
- **Documented**：有可追溯的說明與結果入口。
- **Partial**：該列涵蓋的能力仍有未整合或未驗證部分，明列於最後一欄。

| 分類 | 範圍 | 狀態 | Partial 邊界／未完成項目 |
|---|---|---|---|
| Platform | API submission、背景 polling worker、MPI dispatch／rank execution／terminal collection | Implemented · Validated · Documented · Partial | 9/22 自動結果回收與重啟接續已驗證；仍缺 artifact storage、跨 DB／Redis 原子交易與 full lifecycle state machine |
| Distributed Compute | MPI JobSet、Ray tasks／recovery、Slurm multi-node MPI | Implemented · Validated · Documented · Partial | 各自獨立；Ray／Slurm 未接 API；Ray retry evidence 到 RUNNING，Slurm 歷史 compute VM 已移除 |
| GPU / AI Performance | 13M causal LM training／CUDA profiling、歷史 DDP／vLLM／NCCL | Implemented · Validated · Documented · Partial | 單 L4 time-sharing、byte corpus；無 pretrained LLM 品質、multi-node GPU scaling／RDMA 結論 |
| Scheduling | Kueue queue／quota／priority／preemption／TAS | Implemented · Validated · Documented · Partial | 單實體 GPU node 的 quota／placement 實驗；無 multi-node／cross-zone TAS 驗證 |
| Observability | API metrics、Prometheus／Grafana／DCGM 設定與歷史監控 | Implemented · Validated · Documented · Partial | 缺主 E2E per-job metrics／result 關聯；舊 P100 dashboard evidence 與目前 L4 分開 |
| Infrastructure | Terraform、bootstrap、Helm、Kustomize、Argo CD | Implemented · Validated · Documented · Partial | 全新 CPU-only cluster 已完成 Terraform、controllers、queues、Secrets、platform apply／acceptance／destroy；Spot GPU rehearsal 被全域 quota 阻擋並清理，尚缺全新 GPU MPI 執行、remote state 與 Argo CD 對齊 |
| Security | Namespace RBAC、Pod hardening、NetworkPolicy manifests | Implemented · Validated · Documented · Partial | 隔離 Calico GKE 已驗證 ingress packet allow／deny／recovery；主 cluster enforcement、egress／跨 namespace 與全平台 hardening未完成 |
| Troubleshooting | Kueue、JobSet、Ray、Slurm、NCCL failure-domain 定位 | Implemented · Validated · Documented · Partial | 有 failure scripts／hooks 與紀錄；單 GPU node 無 node failover，Slurm 未驗證恢復，非完整 HA 認證 |
```

## 已有結果與解讀

### 這一課的結果直接看哪裡

本課原本的完整教學、程式示例、結果與解讀已放回本頁下方，不再用縮短版取代它。命令是當時操作或語法示例，**不是要求你現在再執行**。

概念例子的輸出只說明程式／工具行為，不冒充 VM 實測；原文沒留下的實測數值就維持未知，不用預期值補造。舊環境名稱、日期、成功與失敗照原文保留。

## 原始完整教材與當時輸出

以下全文恢復自改寫前版本。舊操作、IP、映像與「目前」指當時環境；其中要求執行／練習的文字保留作歷史教學，**不代表現在還要你操作**。較新的平台行為以頁首補充為準，舊結果不改名成新結果。

另有[可渲染的原版 Markdown](<../history/20260922-before-current/week12/Day4-Linux-Historical-Performance-Analysis.md>)；僅校正該副本搬移後的相對連結。下面正文原樣保留，沒有縮寫或刪掉输出。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Linux 診斷方法繼續適用；舊 perf／strace／CPU 數據不代表主 MPI 的自動 profiling。
> **閱讀順序**：先學本文基礎，再讀[Week12 現行對照與檢核](../learning-guide.md#week12)及[對應現行入口](../performance/performance-report.md)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week12 Day4 - Linux Historical Performance Analysis

## 對應檔案

本篇以概念、命令列操作或文內範例為主，未保存對應的獨立程式／設定檔。

延伸對照文件：[performance-report](../performance/performance-report.md)。

---

## 目標

本章節學習使用 `sar`（System Activity Reporter）分析 Linux 系統歷史效能資料，了解 `sar` 的工作原理，以及如何查看 CPU、Memory、Disk、Network 的歷史資訊。

完成本章後，可以回答：

- `sar` 是什麼？
- `sar` 與 `top` 有什麼差異？
- `sar` 的資料從哪裡來？
- `sysstat` 與 `sadc` 的角色是什麼？
- 為什麼 `sar` 看不到剛剛幾秒鐘前的 CPU 尖峰？

---

# 今日學習重點

- 認識 Historical Performance Analysis
- 了解 `sar` 工作原理
- 了解 `sysstat`、`sadc`
- systemd timer
- `sar -u`
- `sar -P ALL`
- Production Incident Analysis

---

# Lab Environment

OS

```text
Ubuntu 24.04
```

CPU

```text
4 vCPU
```

Memory

```text
16GB
```

---

# 為什麼需要 sar？

前幾天學過：

- top
- free
- vmstat
- iostat

這些工具都有共同特性：

> **只能查看目前系統狀態。**

例如：

今天上午收到通知：

```
昨天晚上 22:30 API Timeout
```

登入主機：

```bash
top
```

看到：

```
CPU Idle 95%
```

並不能代表：

```
昨天晚上 CPU 沒有滿載。
```

因此需要：

```
sar
```

查看歷史資料。

---

# sar 是什麼？

sar

(System Activity Reporter)

屬於：

```
sysstat
```

工具之一。

用途：

讀取 Linux 歷史效能資料。

---

# sar 的工作流程

```
systemd timer
        │
        ▼
sysstat-collect.timer
        │
        ▼
sysstat-collect.service
        │
        ▼
sadc
        │
        ▼
/var/log/sysstat/saXX
        │
        ▼
sar
```

重點：

- `sar` 不負責收集資料。
- `sadc` 才是真正收集資料。
- `sar` 只是讀取 `saXX`。

---

# Step1：確認 sar

查看版本：

```bash
sar -V
```

---

# Step2：確認 sysstat

查看：

```bash
systemctl status sysstat
```

若尚未啟用：

```bash
sudo systemctl enable --now sysstat
```

---

# Step3：確認 Timer

```bash
systemctl list-timers | grep sysstat
```

Ubuntu 24.04：

```
sysstat-collect.timer
```

代表：

系統定期收集資料。

---

# Step4：查看歷史資料

查看：

```bash
ls -lh /var/log/sysstat/
```

例如：

```
sa04
```

代表：

本月第 4 天收集的資料。

---

# Ubuntu 預設收集頻率

查看：

```bash
systemctl cat sysstat-collect.timer
```

重要設定：

```text
OnCalendar=*:00/10
```

代表：

```
每 10 分鐘
```

收集一次。

因此：

```
sar
```

較適合：

- Production Trend
- Incident Analysis

而不是：

```
幾秒鐘內的 CPU 尖峰
```

---

# Step5：查看 CPU

```bash
sar -u
```

重要欄位：

| 欄位 | 說明 |
|------|------|
| %user | User Space CPU |
| %system | Kernel CPU |
| %iowait | Waiting Disk |
| %idle | CPU Idle |

---

# Step6：查看每顆 CPU

```bash
sar -P ALL
```

與：

```
mpstat
```

不同：

- mpstat：即時
- sar：歷史

---

# sar 與其他工具

| 工具 | 用途 |
|------|------|
| top | 即時 CPU / Memory |
| free | 即時 Memory |
| vmstat | 即時 CPU / Memory / IO |
| iostat | 即時 Disk |
| pidstat | 即時 Process |
| sar | 歷史效能分析 |

---

# Production Incident

例如：

```
昨天晚上 22:30 API Timeout
```

分析流程：

```
確認時間
      │
      ▼
sar
      │
CPU 是否異常？
      │
      ▼
Memory 是否異常？
      │
      ▼
Disk 是否異常？
      │
      ▼
Network 是否異常？
      │
      ▼
若需要即時分析
      │
      ▼
top
pidstat
perf
strace
```

---

# 今日重點

- `sar` 是歷史分析工具。
- `sar` 不負責收集資料。
- `sadc` 才是真正收集資料。
- Ubuntu 預設透過 systemd timer 每 10 分鐘收集一次。
- `sar` 適合分析長時間趨勢，不適合分析幾秒鐘的尖峰。

---

# Interview

## Q1：`sar` 與 `top` 有什麼差異？

**答：**

`top` 只能查看目前系統狀態；`sar` 可以讀取 `sysstat` 收集的歷史資料，因此適合分析過去某個時間點的 CPU、Memory、Disk、Network 狀況。

---

## Q2：`sar` 的資料是哪裡來的？

**答：**

`sar` 本身不會收集資料，而是讀取 `sysstat` 使用 `sadc` 定期收集並寫入 `/var/log/sysstat/saXX` 的歷史效能資料。在 Ubuntu 24.04 中，預設由 `sysstat-collect.timer` 每 10 分鐘觸發一次資料收集。
