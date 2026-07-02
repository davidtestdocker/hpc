# Week 3 Day 3－Image 與 Container

## 今日目標

理解 Docker Image 與 Docker Container 的差異，以及 Container 的生命週期。

---

# Image 是什麼？

Image 是 Docker 的模板（Template）。

例如：

- ubuntu:24.04
- python:3.12
- nginx:latest

Image 本身不能執行，它只是建立 Container 的基礎。

---

# Container 是什麼？

Container 是 Image 的執行實體（Running Instance）。

關係如下：

```
Image
    │
    ▼
Container
```

一個 Image 可以建立多個 Container。

---

# docker pull

```bash
docker pull ubuntu:24.04
```

作用：

- 從 Docker Registry 下載 Image
- 不建立 Container
- 不啟動 Container

---

# docker run

```bash
docker run -it ubuntu:24.04
```

作用：

- 使用 Image 建立新的 Container
- 啟動 Container
- 執行預設主程序（本次為 `/bin/bash`）

---

# docker ps

查看目前執行中的 Container。

停止的 Container 不會顯示。

---

# docker ps -a

查看所有 Container。

包含：

- Running
- Exited

---

# Container 的生命週期

本次實驗：

```
docker pull
        │
        ▼
Image
        │
docker run
        ▼
Running Container
        │
exit
        ▼
Exited Container
```

Container 並沒有被刪除，只是停止執行。

---

# Main Process

Container 的生命週期與主程序（Main Process）綁定。

本次主程序為：

```
/bin/bash
```

當執行：

```bash
exit
```

`/bin/bash` 結束，因此 Container 也停止。

---

# 與 HPC AI Performance Engineering Platform 的關聯

未來平台中的所有服務，例如：

- FastAPI
- Prometheus
- Grafana
- Benchmark Worker
- vLLM

都會以 Docker Container 執行。

每個服務都有自己的 Main Process。

若 Main Process 結束，Container 就會停止，因此 Kubernetes 會負責監控與重新啟動 Container。

---

# 今日重點

- Image 是模板。
- Container 是 Image 的執行實體。
- `docker pull` 只下載 Image。
- `docker run` 建立並啟動新的 Container。
- `docker ps` 查看執行中的 Container。
- `docker ps -a` 查看所有 Container。
- Container 的生命週期由 Main Process 決定。
