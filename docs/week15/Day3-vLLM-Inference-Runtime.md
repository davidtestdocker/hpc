# Week15 Day3 - vLLM Inference Runtime

## 今日目標

建立可實際運行於 GPU 的 LLM Inference Runtime，並將新加坡 GKE 的 vLLM Runtime Metrics 跨 Cluster 接回台灣既有 Prometheus / Grafana。

本日完成：

- vLLM Inference Runtime
- Qwen 模型載入
- NVIDIA L4 GPU Inference
- OpenAI-compatible API
- Continuous Batching 驗證
- KV Cache 驗證
- Prefix Cache 驗證
- vLLM Prometheus Metrics
- Singapore → Taiwan 跨 VPC Metrics
- Grafana vLLM Dashboard
- GPU Pool 成本控制

---

## 架構

```text
Taiwan GKE - hpc-dev
│
├── ArgoCD
│   ├── Application: hpc-dev
│   └── Application: hpc-gpu-sg
│
├── Prometheus
│
└── Grafana
        ▲
        │
        │ Prometheus Scrape
        │
        │ VPC Peering
        │
Singapore GKE - hpc-gpu-sg
│
├── GPU Node Pool
│   └── NVIDIA L4
│
├── vLLM
│   └── Qwen/Qwen2.5-0.5B-Instruct
│
└── vllm-service
    └── NodePort 30800
```

Metrics Path：

```text
vLLM Pod :8000/metrics
        ↓
vllm-service
        ↓
SG GPU Node :30800
        ↓
VPC Peering
        ↓
Taiwan Prometheus
        ↓
Grafana
```

---

# 1. vLLM Runtime

建立 Helm Chart：

```text
helm/vllm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

使用 Image：

```text
vllm/vllm-openai:latest
```

模型：

```text
Qwen/Qwen2.5-0.5B-Instruct
```

GPU Resource：

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

指定 GPU Node Pool：

```yaml
nodeSelector:
  cloud.google.com/gke-nodepool: gpu-pool
```

---

# 2. vLLM Service

Service 使用 NodePort：

```yaml
service:
  type: NodePort
  port: 8000
  nodePort: 30800
```

Service Template：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
spec:
  type: {{ .Values.service.type }}
  selector:
    app: vllm
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: 8000
      nodePort: {{ .Values.service.nodePort }}
```

Render 驗證：

```bash
helm template vllm helm/vllm | \
grep -nE 'type: NodePort|nodePort: 30800|port: 8000|targetPort: 8000'
```

結果：

```text
type: NodePort
port: 8000
targetPort: 8000
nodePort: 30800
```

Kubernetes Service：

```text
NAME           TYPE       PORT(S)
vllm-service   NodePort   8000:30800/TCP
```

---

# 3. vLLM API

vLLM 啟動後提供 OpenAI-compatible API：

```text
/v1/models
/v1/chat/completions
/metrics
```

模型 API 驗證成功：

```text
Qwen/Qwen2.5-0.5B-Instruct
```

Inference Flow：

```text
HTTP Request
     ↓
vLLM API Server
     ↓
Qwen Model
     ↓
PyTorch / CUDA
     ↓
NVIDIA L4
     ↓
Generated Tokens
```

---

# 4. LLM Inference

LLM Inference 是：

```text
使用已經訓練完成的模型
接收 Prompt
並產生新的 Token
```

Day3 不進行模型訓練，也不更新模型 Weight。

完整流程：

```text
Prompt
  ↓
Tokenizer
  ↓
Model
  ↓
GPU Compute
  ↓
Generated Tokens
  ↓
Response
```

---

# 5. Continuous Batching

同時送出多個 inference requests：

```bash
kubectl -n hpc-platform-dev exec deployment/vllm -- sh -c '
for i in $(seq 1 30); do
  curl -s http://127.0.0.1:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
      \"model\":\"Qwen/Qwen2.5-0.5B-Instruct\",
      \"messages\":[
        {
          \"role\":\"user\",
          \"content\":\"Write a detailed explanation of GPU inference performance bottlenecks. Request $i.\"
        }
      ],
      \"max_tokens\":1024
    }" >/dev/null &
done
wait
'
```

監控：

```bash
while true; do
  date

  kubectl -n hpc-platform-dev exec deployment/vllm -- \
    sh -c 'curl -s http://127.0.0.1:8000/metrics | grep -E "^vllm:(num_requests_running|num_requests_waiting|kv_cache_usage_perc)"'

  sleep 1
done
```

觀察到：

```text
num_requests_running

30
22
2
0
```

代表多個 Request 可以同時進入 vLLM execution batch。

完成的 Request 離開後，Runtime 可以持續利用新的 execution slot，而不是等待整個固定 Batch 一起完成。

---

# 6. KV Cache

KV Cache 用來儲存前面 Token 在 Attention 計算中產生的：

```text
Key
Value
```

目的：

```text
避免每產生一個新 Token
都重新計算前面所有 Token 的 Attention
```

重要 Metric：

```text
vllm:kv_cache_usage_perc
```

測試期間觀察：

```text
0.005645
0.007836
0.001105
0
```

Request 執行期間 KV Cache Usage 上升。

Request 完成後 Usage 回到接近 0。

---

# 7. PagedAttention

PagedAttention 是 vLLM 對 KV Cache 的 Memory Management 機制。

概念類似：

```text
OS Memory Paging
```

不是要求每個 Request 都取得一大塊連續 GPU Memory，而是將 KV Cache 分成較小的 Block / Page。

好處：

```text
降低 GPU Memory 浪費
降低 Fragmentation
提升 KV Cache 使用效率
支援更多 Concurrent Requests
```

vLLM Runtime 中觀察到：

```text
block_size = 16
kv_cache_size_tokens = 1621248
num_gpu_blocks = 101328
gpu_memory_utilization = 0.92
```

---

# 8. Prefix Cache

vLLM 也支援 Prefix Cache。

若不同 Request 具有相同 Prompt Prefix：

```text
相同 Prefix
    ↓
直接重用之前的計算結果
```

重要 Metrics：

```text
vllm:prefix_cache_queries_total
vllm:prefix_cache_hits_total
```

測試期間曾觀察：

```text
local_compute = 886
local_cache_hit = 1424
```

代表部分 Prompt Token 直接命中 Cache。

---

# 9. vLLM Prometheus Metrics

vLLM 原生提供：

```text
/metrics
```

重要 Runtime Metrics：

```text
vllm:num_requests_running
vllm:num_requests_waiting
vllm:kv_cache_usage_perc

vllm:prompt_tokens_total
vllm:generation_tokens_total

vllm:time_to_first_token_seconds
vllm:inter_token_latency_seconds
vllm:request_time_per_output_token_seconds
vllm:e2e_request_latency_seconds

vllm:prefix_cache_queries_total
vllm:prefix_cache_hits_total
```

---

# 10. Taiwan / Singapore Network

Taiwan：

```text
Cluster:
hpc-dev

VPC:
hpc-dev-vpc

Node CIDR:
10.10.0.0/24

Pod CIDR:
10.68.0.0/14
```

Singapore：

```text
Cluster:
hpc-gpu-sg

VPC:
default

Node CIDR:
10.148.0.0/20

Pod CIDR:
10.56.0.0/14
```

兩邊 CIDR 不重疊，因此可以建立 VPC Peering。

---

# 11. VPC Peering

建立 Taiwan → Singapore Peering：

```bash
gcloud compute networks peerings create hpc-dev-to-default \
  --network=hpc-dev-vpc \
  --peer-network=default
```

建立 Singapore → Taiwan Peering：

```bash
gcloud compute networks peerings create default-to-hpc-dev \
  --network=default \
  --peer-network=hpc-dev-vpc
```

確認狀態：

```text
ACTIVE
Connected
```

因此兩個 GKE Cluster 可以透過 Private IP Routing 互相通訊。

---

# 12. Singapore GPU Node Private IP

Singapore GPU Node Internal IP：

```text
10.148.0.9
```

這不是：

```text
vLLM Pod IP
```

也不是：

```text
Service ClusterIP
```

它是：

```text
Singapore GKE GPU Node Internal IP
```

NodePort Endpoint：

```text
10.148.0.9:30800
```

完整路徑：

```text
Taiwan Pod
   ↓
VPC Peering
   ↓
SG GPU Node
10.148.0.9:30800
   ↓
NodePort Service
   ↓
vLLM Pod:8000
```

---

# 13. Firewall Rule

一開始從 Taiwan 測試：

```bash
kubectl -n hpc-platform-dev run sg-metrics-test \
  --rm -it \
  --restart=Never \
  --image=curlimages/curl \
  -- \
  curl -sS --connect-timeout 5 \
  http://10.148.0.9:30800/metrics
```

發生：

```text
Connection timed out
```

原因：

```text
VPC Peering 已存在
但 Singapore VPC Firewall 尚未允許 Taiwan GKE 流量進入 TCP 30800
```

建立 Firewall Rule：

```bash
gcloud compute firewall-rules create allow-hpc-dev-to-vllm-nodeport \
  --network=default \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:30800 \
  --source-ranges=10.10.0.0/24,10.68.0.0/14
```

允許：

```text
Taiwan Node CIDR
10.10.0.0/24

Taiwan Pod CIDR
10.68.0.0/14
```

連線：

```text
TCP 30800
```

---

# 14. Cross-Cluster Metrics Verification

Firewall 建立後重新測試：

```bash
kubectl -n hpc-platform-dev run sg-metrics-test \
  --rm -it \
  --restart=Never \
  --image=curlimages/curl \
  -- \
  curl -sS --connect-timeout 5 \
  http://10.148.0.9:30800/metrics | head -20
```

成功取得：

```text
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter

python_gc_objects_collected_total{generation="0"} ...

# HELP process_virtual_memory_bytes Virtual memory size in bytes
# TYPE process_virtual_memory_bytes gauge
```

代表：

```text
Taiwan GKE
    ↓
VPC Peering
    ↓
Singapore GPU Node
    ↓
NodePort
    ↓
vLLM /metrics
```

整條 Private Metrics Network 成功。

---

# 15. Prometheus Integration

Prometheus Config：

```text
helm/prometheus/templates/configmap.yaml
```

新增：

```yaml
- job_name: vllm-sg

  static_configs:
    - targets:
        - 10.148.0.9:30800
```

使用 Static Target 的原因：

```text
Taiwan Prometheus 的 Kubernetes Service Discovery
只能直接 Discovery 自己 Cluster 的 Service / Endpoint
```

Singapore 是另一個 GKE Cluster，因此本次直接使用：

```text
SG Node Private IP + NodePort
```

作為 Prometheus Scrape Target。

---

# 16. Prometheus YAML Troubleshooting

第一次加入：

```text
vllm-sg
```

時因 YAML Indentation 錯誤導致：

```text
Prometheus
CrashLoopBackOff
```

Log：

```bash
kubectl -n hpc-platform-dev logs <prometheus-pod> --previous
```

錯誤：

```text
Error loading config
yaml: line 65: did not find expected key
```

查看實際 ConfigMap：

```bash
kubectl -n hpc-platform-dev get configmap prometheus \
  -o jsonpath='{.data.prometheus\.yml}' | \
  nl -ba
```

修正：

```text
vllm-sg
```

與其他：

```text
job_name
```

保持同層。

修正後：

```text
prometheus-xxxxxxxxxx-xxxxx
1/1 Running
```

---

# 17. Prometheus Target Verification

Prometheus Target：

```text
job:
vllm-sg
```

Endpoint：

```text
http://10.148.0.9:30800/metrics
```

狀態：

```text
1 / 1 up
UP
```

代表台灣 Prometheus 已正式定期 Scrape Singapore vLLM。

---

# 18. PromQL Verification

PromQL：

```promql
vllm:num_requests_running{job="vllm-sg"}
```

成功取得：

```text
instance="10.148.0.9:30800"
job="vllm-sg"
model_name="Qwen/Qwen2.5-0.5B-Instruct"
```

因此確認：

```text
vLLM Runtime Metric
        ↓
Singapore NodePort
        ↓
VPC Peering
        ↓
Taiwan Prometheus
```

整條鏈路成功。

---

# 19. Grafana Dashboard

直接透過 Grafana UI 建立 vLLM Runtime Panels。

---

## vLLM Running Requests

```promql
vllm:num_requests_running{job="vllm-sg"}
```

用途：

```text
目前正在 GPU Runtime 中執行的 Inference Request 數量
```

---

## vLLM Waiting Requests

```promql
vllm:num_requests_waiting{job="vllm-sg"}
```

用途：

```text
目前正在等待進入執行的 Request 數量
```

---

## vLLM KV Cache Usage

```promql
vllm:kv_cache_usage_perc{job="vllm-sg"}
```

Unit：

```text
Percent (0-1)
```

用途：

```text
觀察目前 GPU KV Cache 使用比例
```

---

## vLLM Avg TTFT

TTFT：

```text
Time To First Token
```

Query：

```promql
rate(vllm:time_to_first_token_seconds_sum{job="vllm-sg"}[5m])
/
rate(vllm:time_to_first_token_seconds_count{job="vllm-sg"}[5m])
```

用途：

```text
從 Request 送出
到第一個 Token 產生
平均需要多久
```

---

## vLLM Avg E2E Latency

```promql
rate(vllm:e2e_request_latency_seconds_sum{job="vllm-sg"}[5m])
/
rate(vllm:e2e_request_latency_seconds_count{job="vllm-sg"}[5m])
```

用途：

```text
完整 Inference Request
從開始到全部完成的平均時間
```

---

## vLLM Avg Inter-Token Latency

```promql
rate(vllm:inter_token_latency_seconds_sum{job="vllm-sg"}[5m])
/
rate(vllm:inter_token_latency_seconds_count{job="vllm-sg"}[5m])
```

用途：

```text
模型開始輸出後
每兩個 Generated Token 之間的平均延遲
```

數值越低代表 Decode 越快。

---

## vLLM Generation Tokens/s

```promql
rate(vllm:generation_tokens_total{job="vllm-sg"}[5m])
```

用途：

```text
觀察 vLLM 每秒實際產生多少 Output Tokens
```

---

# 20. Grafana Runtime Verification

從 Singapore vLLM 同時送出 10 個 Requests：

```bash
kubectl \
  --context=gke_project-4b82f780-0a12-4087-b94_asia-southeast1-a_hpc-gpu-sg \
  -n hpc-platform-dev \
  exec deployment/vllm -- sh -c '
for i in $(seq 1 10); do
  curl -s http://127.0.0.1:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
      \"model\":\"Qwen/Qwen2.5-0.5B-Instruct\",
      \"messages\":[
        {
          \"role\":\"user\",
          \"content\":\"Explain GPU inference bottlenecks. Request $i.\"
        }
      ],
      \"max_tokens\":256
    }" >/dev/null &
done
wait
'
```

Grafana 實際觀察：

```text
vLLM Generation Tokens/s
8.98 tokens/s

vLLM Avg Inter-Token Latency
5.41 ms

vLLM Avg E2E Latency
1.43 s

vLLM Waiting Requests
0

vLLM Running Requests
0
```

Running / Waiting 回到：

```text
0
```

代表測試 Requests 已全部完成。

KV Cache Usage 最後回到：

```text
0
```

代表目前沒有 Active Inference Request 使用 KV Cache。

---

# 21. Kubernetes Service Environment Variable Collision

Day3 曾遇到 vLLM 啟動失敗。

原本 Service 名稱：

```text
vllm
```

Kubernetes 會自動建立 Service Environment Variable：

```text
VLLM_PORT=tcp://<ClusterIP>:8000
```

但 vLLM 本身也使用：

```text
VLLM_PORT
```

因此 vLLM 啟動時錯誤：

```text
ValueError:
VLLM_PORT 'tcp://...:8000' appears to be a URI
```

修正：

```text
Service Name

vllm
↓
vllm-service
```

Deployment 名稱保持：

```text
vllm
```

修正後：

```text
Starting vLLM server on http://0.0.0.0:8000
Application startup complete.
```

---

# 22. Day3 Final Architecture

```text
Qwen/Qwen2.5-0.5B-Instruct
              ↓
            vLLM
              ↓
       PyTorch / CUDA
              ↓
         NVIDIA L4
              ↓
       Inference API
              ↓
     Runtime Metrics
              ↓
        /metrics:8000
              ↓
      vllm-service
              ↓
       NodePort 30800
              ↓
      SG GPU Node IP
        10.148.0.9
              ↓
        VPC Peering
              ↓
    Taiwan Prometheus
              ↓
          Grafana
```

---

# 23. Day3 完成成果

Week15 Day3 完成：

```text
GPU LLM Inference Runtime
+
vLLM Runtime
+
Continuous Batching
+
KV Cache
+
PagedAttention
+
Prefix Cache
+
Prometheus Metrics
+
Cross-Cluster Private Networking
+
Centralized Grafana Monitoring
```

今天不只是：

```text
模型可以跑
```

而是完成：

```text
GPU Inference Runtime
        +
Runtime Observability
        +
Cross-Cluster Monitoring
```

---

# 24. GPU Cost Control

Day3 完成後將 Singapore GPU Pool Scale To Zero：

```bash
gcloud container clusters resize hpc-gpu-sg \
  --node-pool=gpu-pool \
  --num-nodes=0 \
  --zone=asia-southeast1-a
```

需要重新執行 GPU Workload 時再 Scale Up：

```bash
gcloud container clusters resize hpc-gpu-sg \
  --node-pool=gpu-pool \
  --num-nodes=1 \
  --zone=asia-southeast1-a
```

注意：

```text
GPU Node 被重新建立後
Internal IP 可能改變
```

目前 Prometheus 使用：

```text
10.148.0.9:30800
```

作為 Static Target。

因此 Node 重建後，需要重新確認 GPU Node Internal IP，必要時更新 Prometheus Target。

---

# Interview Review

## Q1：vLLM 解決什麼問題？

vLLM 是專門用於 LLM Inference 的 Runtime / Serving Engine。

它將已訓練完成的模型部署到 GPU 上進行推論，並透過：

```text
KV Cache
PagedAttention
Continuous Batching
Prefix Cache
```

提升 GPU Memory 使用效率、Concurrent Request 處理能力與 Inference Throughput。

---

## Q2：為什麼台灣 Prometheus 可以監控 Singapore GKE 的 vLLM？

因為 Taiwan VPC：

```text
hpc-dev-vpc
```

與 Singapore VPC：

```text
default
```

透過 VPC Peering 建立 Private Routing。

Singapore vLLM 再透過：

```text
NodePort 30800
```

暴露：

```text
/metrics
```

因此 Taiwan Prometheus 可以直接 Scrape：

```text
10.148.0.9:30800/metrics
```

形成：

```text
Singapore vLLM
      ↓
NodePort
      ↓
VPC Peering
      ↓
Taiwan Prometheus
      ↓
Grafana
```
