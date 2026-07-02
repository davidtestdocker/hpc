# Week 3 Day 6－Container 化 Monitoring Framework

## 今日目標

將 `monitoring/process_monitor.py` 打包進 Docker Image，並透過 Docker Compose 在 Container 中執行。

---

# Dockerfile

本日 Dockerfile：

```dockerfile
FROM ubuntu:24.04

RUN apt update

RUN apt install -y python3

COPY monitoring /app/monitoring

CMD ["python3","/app/monitoring/process_monitor.py"]
```

---

# RUN

`RUN` 在 Build 階段執行。

例如：

```dockerfile
RUN apt install -y python3
```

代表在建立 Image 時安裝 Python。

安裝結果會保留在 Image 中。

---

# CMD

`CMD` 在 Container 啟動時執行。

例如：

```dockerfile
CMD ["python3","/app/monitoring/process_monitor.py"]
```

代表 Container 啟動後，主程序為：

```text
python3 /app/monitoring/process_monitor.py
```

---

# Build Image

```bash
docker build -f docker/Dockerfile -t hpc-monitor:v5 .
```

Image 由原本約 117MB 增加至約 273MB。

原因是 Image 中安裝了 Python。

---

# Docker Compose

`compose.yaml` 指向：

```yaml
services:
  monitor:
    image: hpc-monitor:v5
```

啟動：

```bash
docker compose up
```

輸出：

```text
PID COMMAND
1   python3
7   ps
```

代表 `process_monitor.py` 已在 Container 內成功執行。

---

# 重要觀察：Container Namespace

Container 中執行 `ps` 時，只會看到 Container 內部 Process。

因此本次看到：

```text
1 python3
7 ps
```

而不是 Host VM 上所有 Process。

這代表 Container 有自己的 Process Namespace。

---

# 今日重點

- `RUN` 用於 Build 階段，結果保留在 Image。
- `CMD` 用於 Container 啟動階段，決定 Main Process。
- Monitoring Framework 已成功在 Container 中執行。
- Container 預設只能看到自己的 Process，不會看到 Host 全部 Process。

---

# 與 HPC AI Performance Engineering Platform 的關聯

本日完成第一個真正容器化的元件：

```text
Monitoring Framework
        │
        ▼
Docker Image
        │
        ▼
Docker Compose
        │
        ▼
Monitoring Container
```

這是後續 FastAPI、Benchmark Worker、Analysis Engine 容器化的範本。
