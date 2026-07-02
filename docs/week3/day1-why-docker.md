# Week 3 Day 1－為什麼需要 Docker？

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
