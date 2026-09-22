<!-- readable-curriculum: 2026-09-22 -->
# Week3 Day1 — 為何容器化

[本週基礎](README.md) · [本週目錄](README.md) · [下一課](<day2-install-docker.md>) · [全程導讀](../learning-guide.md)

## 本頁內容核對（2026-09-22）

**已核對本課程式／設定、文內操作與引用結果；證據層級：架構概念，無本課執行結果。** 這是文件核對，不是重跑環境；沒有要求你再開 VM 或做本機測試。全套進度見[逐篇稽核清單](../audits/curriculum-content-audit.md)，尚未核對的頁面不算完成。

## 概念解說與現行差異

容器共享 host kernel、硬體和外部依賴，不能保證一個服務更新永不影響其他服務。Kubernetes 可以使用 containerd 等 runtime，不以 Docker Engine 為必要條件；原文「Docker 是所有服務執行環境」只對當時入門設計成立。

## 程式／設定與來源

本次核對：[docker/Dockerfile](<../../docker/Dockerfile>)、[compose.yaml](<../../compose.yaml>)

## 已有結果與解讀

來源：[記錄／示例原文](<../../docker/Dockerfile>)。下面逐字摘錄來源中的內容；它是輸出、程式或命令示例，依本頁證據層級區分，不一律視為實測。

```text
FROM python:3.12-slim
```

目前 Dockerfile 的基底是 python:3.12-slim，預設 CMD 啟動 Uvicorn；這是原始碼設定核對，不是新 image build／run 成功記錄。

**仍缺的證據／不能證明的事：** 本課沒有 build／run 原始 log、環境隔離對照實驗或同 image 跨機器一致性驗收。

## 原始完整教材與當時輸出

以下原文完整保留，包含原本的命令、範例、成功與失敗；其中過度推論或現行差異已在頁首逐項修正。舊文的「目前」指當時，精確日期未保存時不補猜；命令不用重新執行。

<!-- original-week-body -->
<!-- current-learning-map -->
> **版本同步（2026-09-22）**：下方正文保留本日原始學習／實驗紀錄，不作為現行環境操作手冊。
> **本週現況**：Compose 是本機學習環境，不等於 GKE 主平台或 MPI 端到端驗收。
> **閱讀順序**：先學本文基礎，再讀[Week3 現行對照與檢核](../learning-guide.md#week3)及[對應現行入口](../../compose.yaml)。
> **操作提醒**：舊 IP、context、映像及 apply／destroy 指令不可直接照跑；先確認目標環境與現行 runbook。
<!-- /current-learning-map -->

# Week 3 Day 1－為什麼需要 Docker？

## 對應檔案

以下連結指向儲存庫目前版本，供對照本文；歷史步驟與現況可能不同。

- [docker/Dockerfile](../../docker/Dockerfile)：容器映像建置

---

## 今日目標

理解 Docker 在 HPC AI Performance Engineering Platform 中存在的目的。

Docker 並不是學習目標，而是平台部署與管理的工具。

---

# 為什麼需要 Docker？

目前平台直接在 Ubuntu 上執行：

```text
Ubuntu

├── Python
├── Monitoring Framework
├── FastAPI（未來）
├── Prometheus（未來）
├── Grafana（未來）
└── Benchmark Worker（未來）
```

所有服務都安裝在同一個作業系統中。

當服務越來越多，就容易出現：

- 套件衝突
- Python 版本衝突
- 升級影響其他服務
- 難以部署
- 難以回滾

---

# Docker 解決什麼問題？

Docker 提供：

**Isolation（隔離）**

每一個服務都有自己的執行環境。

例如：

```text
Ubuntu

├── FastAPI Container
│       Python 3.12
│
├── Prometheus Container
│
├── Grafana Container
│
└── Benchmark Worker Container
```

每個 Container 彼此獨立。

其中一個服務更新，不會影響其他服務。

---

# Image 與 Container

Docker 有兩個重要概念：

Image：

```
Template
```

Container：

```
Running Instance
```

兩者關係類似：

```
Program
        │
        ▼
Process
```

Docker：

```
Image
        │
        ▼
Container
```

Image 可以建立多個 Container。

---

# Docker 在平台中的角色

未來平台：

```
Control Node

├── FastAPI Container
├── Prometheus Container
├── Grafana Container
└── Analysis Engine Container

Compute Node

├── Benchmark Worker Container
├── vLLM Container
├── Node Exporter Container
└── DCGM Exporter Container
```

Docker 是所有平台服務的執行環境。

---

# 今日重點

- Docker 的核心價值是隔離（Isolation）。
- Container 可以避免不同服務互相影響。
- Image 是 Container 的模板。
- Container 是真正執行中的服務。
- Docker 是 Kubernetes 的基礎。

---

# 與 HPC AI Performance Engineering Platform 的關聯

本平台未來所有核心元件都會以 Container 執行，包括：

- Monitoring Framework
- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

Docker 讓每個服務可以：

- 獨立部署
- 獨立升級
- 獨立回滾
- 獨立除錯

降低平台維護成本，提升部署一致性。

---

# 面試重點

如果沒有 Docker：

- 不同服務可能產生版本衝突。
- 升級一個服務可能影響整個系統。
- 測試新版本風險較高。

使用 Docker 後：

- 每個服務擁有自己的執行環境。
- 可以快速建立、測試、刪除 Container。
- 適合大型平台的部署與維護。
