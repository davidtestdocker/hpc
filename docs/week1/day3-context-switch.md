# Week 1 Day 3－Context Switch（上下文切換）

## 今日目標

理解 Context Switch 是什麼，以及它為什麼會影響系統效能。

---

# 什麼是 Context Switch？

當 CPU Core 不足以同時執行所有 Process 時，Linux Scheduler 必須在不同 Process 之間切換。

切換前，需要保存目前 Process 的執行狀態。

切換後，需要恢復下一個 Process 的執行狀態。

這個過程稱為 Context Switch。

---

# 為什麼需要 Context Switch？

目前實驗環境：

- CPU Core：4

建立五個高 CPU 使用率 Process：

```bash
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
yes > /dev/null &
```

由於 Process 數量超過 CPU Core 數量，Scheduler 必須不停在 Process 之間切換。

---

# 實驗結果

使用：

```bash
top
```

觀察到：

- 五個 `yes` Process 同時存在
- 每個 Process CPU 使用率約 75%～85%

代表 Scheduler 正在公平分配 CPU 時間，而不是讓某一個 Process 長時間獨占 CPU。

---

# Context Switch 的成本

Context Switch 不會執行任何業務邏輯。

它需要：

- 保存目前 Process 狀態
- 載入下一個 Process 狀態
- 恢復執行

因此會消耗 CPU 時間。

Context Switch 越頻繁，可用於真正運算的 CPU 時間就越少。

---

# 今日重點

- Context Switch 是 Linux Scheduler 在 Process 間切換的過程。
- 當 Process 數量超過 CPU Core 數量時，Context Switch 會增加。
- CPU 使用率高，不代表 CPU 都在做有效工作。
- Context Switch 過多會降低整體效能。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的：

- FastAPI
- Benchmark Worker
- Prometheus
- Grafana
- vLLM

都是 Linux Process。

如果 Compute Node 的 CPU 資源不足，Scheduler 會增加 Context Switch。

Context Switch 增加後，可能造成：

- TPS 下降
- TTFT 增加
- Latency 增加

因此，Performance Engineer 在分析 CPU Bottleneck 時，不能只看 CPU 使用率，還必須考慮 Context Switch 是否過於頻繁。
