# 教材逐篇內容稽核

更新：2026-09-22。**已逐篇核對 138／138 篇；尚待核對 0 篇。本輪文件核對完成。** 20 個每週入口另已核對與同步，未計入 138 篇。

重要程式落差、缺證據與驗證邊界見[問題總表](curriculum-findings.md)。完成的是文件核對，不是重跑全部實驗或修復全部程式。

已核對不等於每頁都有 raw log；每頁明列「歷史文內記錄、概念示例、缺證據」與現行差異。既有 `check_curriculum.py` 的連結／hash 通過只證明結構和保存，不等於內容正確。此次不開 VM、不跑 workload、不查雲端。

## 本輪判準

1. 閱讀原課文，而非只看標題或批次補通用結果。
2. 核對提到的程式／設定是否存在、行為及路徑是否一致。
3. 把對應輸出直接放到該課；跨課引用標來源，不當作本課獨立實測。
4. 示例／佔位值不當作執行結果；文內記載不升級為獨立 raw log。
5. 修正頁首解讀與過度結論；原始全文／原始證據不覆寫。缺證據不要求使用者花錢重跑。

## 逐篇狀態

| 課程 | 狀態 | 證據層級／問題 |
|---|---|---|
| [week1/day1-linux-process](<../../docs/week1/day1-linux-process.md>) | 已核對、頁首已修正 | 歷史教材輸出（跨頁接回） |
| [week1/day2-cpu-scheduler](<../../docs/week1/day2-cpu-scheduler.md>) | 已核對、頁首已修正 | 歷史教材數值摘錄 |
| [week1/day3-context-switch](<../../docs/week1/day3-context-switch.md>) | 已核對、頁首已修正 | 歷史教材觀察，缺直接計數 |
| [week1/day4-cpu-utilization](<../../docs/week1/day4-cpu-utilization.md>) | 已核對、頁首已修正 | 歷史教材數值摘錄 |
| [week1/day5-memory](<../../docs/week1/day5-memory.md>) | 已核對、頁首已修正 | 歷史教材數值摘錄 |
| [week1/day6-disk-io](<../../docs/week1/day6-disk-io.md>) | 已核對、頁首已修正 | 歷史教材數值摘錄 |
| [week1/day7-performance-analysis](<../../docs/week1/day7-performance-analysis.md>) | 已核對、頁首已修正 | 概念示例與未落實規劃 |
| [week2/day1-python](<../../docs/week2/day1-python.md>) | 已核對、頁首已修正 | 程式可推導示例，非實機 log |
| [week2/day2-function](<../../docs/week2/day2-function.md>) | 已核對、頁首已修正 | 文內函式示例 |
| [week2/day3-return](<../../docs/week2/day3-return.md>) | 已核對、頁首已修正 | 文內 return 示例 |
| [week2/day4-list](<../../docs/week2/day4-list.md>) | 已核對、頁首已修正 | 文內資料結構示例 |
| [week2/day5-dictionary](<../../docs/week2/day5-dictionary.md>) | 已核對、頁首已修正 | 文內 dict 示例 |
| [week2/day6-subprocess](<../../docs/week2/day6-subprocess.md>) | 已核對、頁首已修正 | 歷史教材輸出（跨頁接回） |
| [week2/day7-stdout](<../../docs/week2/day7-stdout.md>) | 已核對、頁首已修正 | 示例與歷史輸出分開 |
| [week3/day1-why-docker](<../../docs/week3/day1-why-docker.md>) | 已核對、頁首已修正 | 架構概念，無本課執行結果 |
| [week3/day2-install-docker](<../../docs/week3/day2-install-docker.md>) | 已核對、頁首已修正 | 版本佔位示例，非驗收 |
| [week3/day3-image-container](<../../docs/week3/day3-image-container.md>) | 已核對、頁首已修正 | 歷史流程敘述，缺命令結果 |
| [week3/day4-dockerfile](<../../docs/week3/day4-dockerfile.md>) | 已核對、頁首已修正 | 歷史檔案／layer 敘述 |
| [week3/day5-docker-compose](<../../docs/week3/day5-docker-compose.md>) | 已核對、頁首已修正 | 歷史配置與概念示例 |
| [week3/day6-containerize-monitoring](<../../docs/week3/day6-containerize-monitoring.md>) | 已核對、頁首已修正 | 歷史教材保存的容器輸出 |
| [week3/day7-docker-integration](<../../docs/week3/day7-docker-integration.md>) | 已核對、頁首已修正 | 跨課歷史整合摘要 |
| [week4/day1-platform-api-design](<../../docs/week4/day1-platform-api-design.md>) | 已核對、頁首已修正 | 歷史 API 回應摘錄 |
| [week4/day2-rest-api-design](<../../docs/week4/day2-rest-api-design.md>) | 已核對、頁首已修正 | 歷史 REST 回應摘錄 |
| [week4/day3-job-identity](<../../docs/week4/day3-job-identity.md>) | 已核對、頁首已修正 | UUID 佔位示例，非真實 job 證據 |
| [week4/day4-memory-queue](<../../docs/week4/day4-memory-queue.md>) | 已核對、頁首已修正 | 歷史模擬 worker 結果 |
| [week4/day5-dockerize-api](<../../docs/week4/day5-dockerize-api.md>) | 已核對、頁首已修正 | 歷史環境變數摘錄，現行 Compose 有差異 |
| [week4/day6-monitoring-integration](<../../docs/week4/day6-monitoring-integration.md>) | 已核對、頁首已修正 | 歷史 health／log／metrics 摘錄 |
| [week5/day1-redis-foundation](<../../docs/week5/day1-redis-foundation.md>) | 已核對、頁首已修正 | 歷史 Redis ping 摘錄 |
| [week5/day2-redis-persistence](<../../docs/week5/day2-redis-persistence.md>) | 已核對、頁首已修正 | 有日期與環境的持久化驗收 |
| [week5/day3-reliable-worker-state-machine](<../../docs/week5/day3-reliable-worker-state-machine.md>) | 已核對、頁首已修正 | 有日期的 queue 清理結果 |
| [week5/day4-stuck-job-recovery](<../../docs/week5/day4-stuck-job-recovery.md>) | 已核對、頁首已修正 | 有日期的 worker 重啟接續結果 |
| [week5/day5-retry-strategy-and-deadletter-que](<../../docs/week5/day5-retry-strategy-and-deadletter-que.md>) | 已核對、頁首已修正 | 有日期的模擬失敗與 DLQ 結果 |
| [week5/day6-postgresql-foundation](<../../docs/week5/day6-postgresql-foundation.md>) | 已核對、頁首已修正 | 歷史 SQL 示例與資料庫文字摘錄 |
| [week5/day7-sqlalchemy-foundation](<../../docs/week5/day7-sqlalchemy-foundation.md>) | 已核對、頁首已修正 | 有日期的 PostgreSQL 終態核對 |
| [week6/Day1_Kubernetes_Foundation](<../../docs/week6/Day1_Kubernetes_Foundation.md>) | 已核對、頁首已修正 | 概念課與副本設定，非故障驗收 |
| [week6/Day2_Pod_Foundation](<../../docs/week6/Day2_Pod_Foundation.md>) | 已核對、頁首已修正 | 概念課，無 Pod lifecycle 實測 |
| [week6/Day3_Deployment_Foundation](<../../docs/week6/Day3_Deployment_Foundation.md>) | 已核對、頁首已修正 | 副本與更新策略設定，非擴縮實測 |
| [week6/Day4_Service_Foundation](<../../docs/week6/Day4_Service_Foundation.md>) | 已核對、頁首已修正 | Service 設定對照，無負載分配實測 |
| [week6/Day5_K3s_Foundation](<../../docs/week6/Day5_K3s_Foundation.md>) | 已核對、頁首已修正 | 歷史 K3s 節點輸出摘錄 |
| [week6/Day6_Deploy_API_and_Redis](<../../docs/week6/Day6_Deploy_API_and_Redis.md>) | 已核對、頁首已修正 | 歷史 startup log 摘錄及設定差異 |
| [week6/Day7_Complete_Platform_on_Kubernetes](<../../docs/week6/Day7_Complete_Platform_on_Kubernetes.md>) | 已核對、頁首已修正 | 後來 CPU-only GKE 驗收，與舊 K3s 分開 |
| [week7/Day1_ConfigMap](<../../docs/week7/Day1_ConfigMap.md>) | 已核對、頁首已修正 | 歷史 describe 摘錄 |
| [week7/Day2_Secret](<../../docs/week7/Day2_Secret.md>) | 已核對、頁首已修正 | 歷史 Secret 中繼資料示例 |
| [week7/Day3_Resource_Requests_Limits_QoS](<../../docs/week7/Day3_Resource_Requests_Limits_QoS.md>) | 已核對、頁首已修正 | 歷史資源與 QoS 摘錄 |
| [week7/Day4_Liveness_and_Readiness_Probe](<../../docs/week7/Day4_Liveness_and_Readiness_Probe.md>) | 已核對、頁首已修正 | 歷史故障描述，無完整 events |
| [week7/Day5_Service_Types_NodePort](<../../docs/week7/Day5_Service_Types_NodePort.md>) | 已核對、頁首已修正 | 歷史 NodePort HTTP 摘錄 |
| [week7/Day6_Ingress_Traefik](<../../docs/week7/Day6_Ingress_Traefik.md>) | 已核對、頁首已修正 | 歷史 host-routing 回覆 |
| [week7/Day7_Horizontal_Pod_Autoscaler](<../../docs/week7/Day7_Horizontal_Pod_Autoscaler.md>) | 已核對、頁首已修正 | 歷史 HPA 觀察 |
| [week8/Day1_GitOps_Foundation](<../../docs/week8/Day1_GitOps_Foundation.md>) | 已核對、頁首已修正 | 概念與 Argo 設定 |
| [week8/Day2_Helm_Foundation](<../../docs/week8/Day2_Helm_Foundation.md>) | 已核對、頁首已修正 | 歷史 scaffold 渲染示例 |
| [week8/Day3_Helmize_Platform](<../../docs/week8/Day3_Helmize_Platform.md>) | 已核對、頁首已修正 | 參數化示例與現存模板 |
| [week8/Day4_Helm_Advanced](<../../docs/week8/Day4_Helm_Advanced.md>) | 已核對、頁首已修正 | 歷史 revision 敘述 |
| [week8/Day5_Kustomize_Foundation](<../../docs/week8/Day5_Kustomize_Foundation.md>) | 已核對、頁首已修正 | 歷史三環境 render 描述 |
| [week8/Day6-Helm-Kustomize-Integration](<../../docs/week8/Day6-Helm-Kustomize-Integration.md>) | 已核對、頁首已修正 | 歷史錯誤與整合設定 |
| [week8/Day7-GitOps_Multi_Environment_Integration](<../../docs/week8/Day7-GitOps_Multi_Environment_Integration.md>) | 已核對、頁首已修正 | Expected 回覆，非現行部署證據 |
| [week9/Day1-Terraform](<../../docs/week9/Day1-Terraform.md>) | 已核對、頁首已修正 | 歷史版本與掛載摘要 |
| [week9/Day2-Terraform-Language-Foundation](<../../docs/week9/Day2-Terraform-Language-Foundation.md>) | 已核對、頁首已修正 | 歷史 validate／plan 摘錄 |
| [week9/Day3-Terraform-Apply-State-Resource-Lifecycle](<../../docs/week9/Day3-Terraform-Apply-State-Resource-Lifecycle.md>) | 已核對、頁首已修正 | 歷史 apply 與取消 destroy |
| [week9/Day4-Terraform-Output-Resource-Reference](<../../docs/week9/Day4-Terraform-Output-Resource-Reference.md>) | 已核對、頁首已修正 | 歷史 output 摘錄 |
| [week9/Day5-Terraform-Module-Refactor](<../../docs/week9/Day5-Terraform-Module-Refactor.md>) | 已核對、頁首已修正 | 歷史 state 搬移／plan 摘錄 |
| [week9/Day6-Terraform-Network-Module](<../../docs/week9/Day6-Terraform-Network-Module.md>) | 已核對、頁首已修正 | 設定與 plan 敘述，無 apply 證據 |
| [week9/Day7-Terraform-Multi-Environment](<../../docs/week9/Day7-Terraform-Multi-Environment.md>) | 已核對、頁首已修正 | 歷史 sandbox 清理敘述 |
| [week9/Day8-GKE-Cluster-withTerraform](<../../docs/week9/Day8-GKE-Cluster-withTerraform.md>) | 已核對、頁首已修正 | CPU-only 後續驗收 |
| [week10/Day1-CICD-Foundation](<../../docs/week10/Day1-CICD-Foundation.md>) | 已核對、頁首已修正 | 規劃與 workflow 靜態核對 |
| [week10/Day2-First-GitHub-ActionsCI-Pipeline](<../../docs/week10/Day2-First-GitHub-ActionsCI-Pipeline.md>) | 已核對、頁首已修正 | 歷史 CI Success 敘述 |
| [week10/Day3-CodeQuality-withRuff](<../../docs/week10/Day3-CodeQuality-withRuff.md>) | 已核對、頁首已修正 | 歷史 lint 結果敘述 |
| [week10/Day4-Pytest-API-Testing-Foundation](<../../docs/week10/Day4-Pytest-API-Testing-Foundation.md>) | 已核對、頁首已修正 | 歷史依賴失敗與現行測試 |
| [week10/Day5-Pytest-MockCI-Integration](<../../docs/week10/Day5-Pytest-MockCI-Integration.md>) | 已核對、頁首已修正 | Mock 設計與成功敘述 |
| [week10/Day6-Docker-Build-inCI](<../../docs/week10/Day6-Docker-Build-inCI.md>) | 已核對、頁首已修正 | 歷史 Docker build 敘述 |
| [week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD](<../../docs/week10/Day7-GitHub-Actions-GitOps-自動部署-ArgoCD.md>) | 已核對、頁首已修正 | 歷史 GitOps 敘述与現行限制 |
| [week11/Day1-建立Prometheus監控平台與Observability-Node-Pool](<../../docs/week11/Day1-建立Prometheus監控平台與Observability-Node-Pool.md>) | 已核對、頁首已修正 | 歷史監控失敗與設定 |
| [week11/Day2-Prometheus-ScrapeJob-Target與PullModel](<../../docs/week11/Day2-Prometheus-ScrapeJob-Target與PullModel.md>) | 已核對、頁首已修正 | 歷史 scrape 格式失敗 |
| [week11/Day3-FastAPI-Application-Metrics](<../../docs/week11/Day3-FastAPI-Application-Metrics.md>) | 已核對、頁首已修正 | 歷史 metrics 摘錄 |
| [week11/Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery](<../../docs/week11/Day4-NodeExporter-GrafanaDashboard-KubernetesServiceDiscovery.md>) | 已核對、頁首已修正 | 歷史兩target文字記錄 |
| [week12/Day1-Linux-CPU-Performance-Analysis](<../../docs/week12/Day1-Linux-CPU-Performance-Analysis.md>) | 已核對、頁首已修正 | 歷史CPU觀察 |
| [week12/Day2-Linux-Memory-Performance-Analysis](<../../docs/week12/Day2-Linux-Memory-Performance-Analysis.md>) | 已核對、頁首已修正 | 歷史記憶體快照 |
| [week12/Day3-Linux-Disk-Performance-Analysis](<../../docs/week12/Day3-Linux-Disk-Performance-Analysis.md>) | 已核對、頁首已修正 | 歷史fio數值 |
| [week12/Day4-Linux-Historical-Performance-Analysis](<../../docs/week12/Day4-Linux-Historical-Performance-Analysis.md>) | 已核對、頁首已修正 | 歷史timer設定，無事故時序 |
| [week12/Day5-Linux-CPU-Benchmark-with-sysbench](<../../docs/week12/Day5-Linux-CPU-Benchmark-with-sysbench.md>) | 已核對、頁首已修正 | 歷史sysbench表格 |
| [week12/Day6-Linux-CPU-Profiling-with-perf](<../../docs/week12/Day6-Linux-CPU-Profiling-with-perf.md>) | 已核對、頁首已修正 | 歷史PMU不可用與概念示例 |
| [week12/Day7-Linux-System-Call-Analysis-with-strace](<../../docs/week12/Day7-Linux-System-Call-Analysis-with-strace.md>) | 已核對、頁首已修正 | syscall概念示例，無完整trace |
| [week13/Day1-FastAPI-API-Benchmark](<../../docs/week13/Day1-FastAPI-API-Benchmark.md>) | 已核對、頁首已修正 | 歷史ApacheBench摘要 |
| [week13/Day2-Redis-Benchmark](<../../docs/week13/Day2-Redis-Benchmark.md>) | 已核對、頁首已修正 | 歷史redis-benchmark表格 |
| [week13/Day3-PostgreSQL-Benchmark](<../../docs/week13/Day3-PostgreSQL-Benchmark.md>) | 已核對、頁首已修正 | 歷史pgbench結果 |
| [week13/Day4-PostgreSQL-Concurrency-Benchmark](<../../docs/week13/Day4-PostgreSQL-Concurrency-Benchmark.md>) | 已核對、頁首已修正 | 歷史併發比較 |
| [week13/day5-resource-monitoring](<../../docs/week13/day5-resource-monitoring.md>) | 已核對、頁首已修正 | 歷史資源取樣 |
| [week13/day6-benchmark-automation](<../../docs/week13/day6-benchmark-automation.md>) | 已核對、頁首已修正 | 歷史runner摘要與程式缺陷 |
| [week13/day7-1-cpu-benchmark](<../../docs/week13/day7-1-cpu-benchmark.md>) | 已核對、頁首已修正 | 歷史CPU結果檔 |
| [week13/day7-2-storage-benchmark](<../../docs/week13/day7-2-storage-benchmark.md>) | 已核對、頁首已修正 | 歷史fio結果檔 |
| [week13/day7-3-network-benchmark](<../../docs/week13/day7-3-network-benchmark.md>) | 已核對、頁首已修正 | 歷史同節點iperf摘要 |
| [week13/day7-4-benchmark-framework](<../../docs/week13/day7-4-benchmark-framework.md>) | 已核對、頁首已修正 | runner實作，無全套原始log |
| [week13/day7-5-benchmark-framework-v2](<../../docs/week13/day7-5-benchmark-framework-v2.md>) | 已核對、頁首已修正 | 歷史PASS文字，現存失敗傳遞缺口 |
| [week13/day7-6-result-integration](<../../docs/week13/day7-6-result-integration.md>) | 已核對、頁首已修正 | 歷史結果目錄敘述 |
| [week13/day7-7-week13-final-report](<../../docs/week13/day7-7-week13-final-report.md>) | 已核對、頁首已修正 | 歷史綜合報告 |
| [week13/day7-benchmark-report](<../../docs/week13/day7-benchmark-report.md>) | 已核對、頁首已修正 | 原頁僅索引，補既有結果 |
| [week14/day2-kubernetes-gpu-scheduling](<../../docs/week14/day2-kubernetes-gpu-scheduling.md>) | 已核對、頁首已修正 | GPU 排程概念，無當日GPU測試 |
| [week14/day3-gpu-monitoring-architecture](<../../docs/week14/day3-gpu-monitoring-architecture.md>) | 已核對、頁首已修正 | 監控架構說明，非執行結果 |
| [week14/Day4-GKE-GPU-Node-Pool-GPU-Scheduling](<../../docs/week14/Day4-GKE-GPU-Node-Pool-GPU-Scheduling.md>) | 已核對、頁首已修正 | 歷史P100 nvidia-smi 摘錄 |
| [week14/Day5-GPU-Metrics-Monitoring-integration](<../../docs/week14/Day5-GPU-Metrics-Monitoring-integration.md>) | 已核對、頁首已修正 | 歷史DCGM故障與metrics |
| [week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification](<../../docs/week14/Day6-gpu-dashboard-establish-and-gpuworkload-verification.md>) | 已核對、頁首已修正 | 歷史P100 dashboard觀察 |
| [week15/Day1—PyTorch-GPU-Runtime](<../../docs/week15/Day1—PyTorch-GPU-Runtime.md>) | 已核對、頁首已修正 | 歷史GPU功能驗證 |
| [week15/Day2-PyTorch-Training-Runtime](<../../docs/week15/Day2-PyTorch-Training-Runtime.md>) | 已核對、頁首已修正 | 歷史合成資料訓練與故障 |
| [week15/Day3-vLLM-Inference-Runtime](<../../docs/week15/Day3-vLLM-Inference-Runtime.md>) | 已核對、頁首已修正 | 歷史vLLM服務與跨區監控 |
| [week15/Day4-Runtime-Abstraction](<../../docs/week15/Day4-Runtime-Abstraction.md>) | 已核對、頁首已修正 | 歷史adapter推論回覆 |
| [week15/Day5-Benchmark-Engine](<../../docs/week15/Day5-Benchmark-Engine.md>) | 已核對、頁首已修正 | 20260816 vLLM JSON |
| [week15/Day6-Performance-Analyzer](<../../docs/week15/Day6-Performance-Analyzer.md>) | 已核對、頁首已修正 | 固定prompts JSON與歷史profiler摘要 |
| [week15/Day7-AI-Runtime-Platform-v1-Integration](<../../docs/week15/Day7-AI-Runtime-Platform-v1-Integration.md>) | 已核對、頁首已修正 | 20260817單L4推論JSON |
| [week16/day1-multi-gpu-fundamentals](<../../docs/week16/day1-multi-gpu-fundamentals.md>) | 已核對、頁首已修正 | 分散式概念，非多GPU成果 |
| [week16/day2-pytorch-ddp](<../../docs/week16/day2-pytorch-ddp.md>) | 已核對、頁首已修正 | 歷史CPU Gloo DDP輸出 |
| [week16/day3-nccl-fundamentals](<../../docs/week16/day3-nccl-fundamentals.md>) | 已核對、頁首已修正 | NCCL概念與單rank版本log |
| [week16/day4-nccl-communication-benchmark](<../../docs/week16/day4-nccl-communication-benchmark.md>) | 已核對、頁首已修正 | 單L4 NCCL原始log |
| [week16/day5-distributed-training-scaling](<../../docs/week16/day5-distributed-training-scaling.md>) | 已核對、頁首已修正 | 歷史CPU scaling摘要 |
| [week17/day1-mpi-fundamentals](<../../docs/week17/day1-mpi-fundamentals.md>) | 已核對、頁首已修正 | 歷史MPI collective輸出 |
| [week17/day2-mpi-performance-benchmark](<../../docs/week17/day2-mpi-performance-benchmark.md>) | 已核對、頁首已修正 | 歷史單機OSU摘要 |
| [week17/day3-hpc-communication-stack](<../../docs/week17/day3-hpc-communication-stack.md>) | 已核對、頁首已修正 | 歷史RDMA不可見檢查 |
| [week17/day4-slurm-multinode-hpc-cluster](<../../docs/week17/day4-slurm-multinode-hpc-cluster.md>) | 已核對、頁首已修正 | 歷史Slurm雙VM啟動與失敗 |
| [week17/day5-ray-kuberay-distributed-computing](<../../docs/week17/day5-ray-kuberay-distributed-computing.md>) | 已核對、頁首已修正 | 歷史RayJob狀態 |
| [week17/day6-cluster-scheduling-integration](<../../docs/week17/day6-cluster-scheduling-integration.md>) | 已核對、頁首已修正 | 歷史排程資源爭用 |
| [week18/day1-linux-network-troubleshooting-baseline](<../../docs/week18/day1-linux-network-troubleshooting-baseline.md>) | 已核對、頁首已修正 | 歷史兩VM網路摘要 |
| [week18/day2-network-quality-bandwidth-latency-mtu](<../../docs/week18/day2-network-quality-bandwidth-latency-mtu.md>) | 已核對、頁首已修正 | 歷史TCP/UDP/ICMP比較 |
| [week18/day3-packet-level-network-failure-troubleshooting](<../../docs/week18/day3-packet-level-network-failure-troubleshooting.md>) | 已核對、頁首已修正 | 歷史refused/timeout故障注入 |
| [week18/day4-kubernetes-network-troubleshooting](<../../docs/week18/day4-kubernetes-network-troubleshooting.md>) | 已核對、頁首已修正 | 歷史空backend／失效IP／未enforce |
| [week18/day5-nccl-transport-debugging](<../../docs/week18/day5-nccl-transport-debugging.md>) | 已核對、頁首已修正 | 單rank NCCL transport raw |
| [week18/day6-gpu-nic-numa-topology](<../../docs/week18/day6-gpu-nic-numa-topology.md>) | 已核對、頁首已修正 | 歷史VM拓樸摘要 |
| [week18/day7-distributed-communication-troubleshooting-playbook](<../../docs/week18/day7-distributed-communication-troubleshooting-playbook.md>) | 已核對、頁首已修正 | 既有案例整理，非新端到端驗收 |
| [week19/day1-gpu-sharing-models](<../../docs/week19/day1-gpu-sharing-models.md>) | 已核對、頁首已修正 | 歷史單L4 sharing配置 |
| [week19/day2-kueue-gpu-admission](<../../docs/week19/day2-kueue-gpu-admission.md>) | 已核對、頁首已修正 | 歷史Kueue准入摘要 |
| [week19/day3-gpu-quota-admission-queue-behavior](<../../docs/week19/day3-gpu-quota-admission-queue-behavior.md>) | 已核對、頁首已修正 | 歷史quota等待與放行 |
| [week19/day4-priority-preemption-multi-tenancy](<../../docs/week19/day4-priority-preemption-multi-tenancy.md>) | 已核對、頁首已修正 | 歷史Kueue preemption事件 |
| [week19/day5-gang-jobset-mpi](<../../docs/week19/day5-gang-jobset-mpi.md>) | 已核對、頁首已修正 | 歷史MPI啟動與gang准入 |
| [week19/day6-topology-aware-gpu-scheduling](<../../docs/week19/day6-topology-aware-gpu-scheduling.md>) | 已核對、頁首已修正 | 歷史TAS placement，執行未完成 |
| [week19/day7-gpu-scheduling-platform-integration](<../../docs/week19/day7-gpu-scheduling-platform-integration.md>) | 已核對、頁首已修正 | 週內多實驗概念整合 |
| [week20/day1-rbac-serviceaccount-least-privilege](<../../docs/week20/day1-rbac-serviceaccount-least-privilege.md>) | 已核對、頁首已修正 | 歷史RBAC HTTP狀態 |
| [week20/day2-pod-image-secret-security](<../../docs/week20/day2-pod-image-secret-security.md>) | 已核對、頁首已修正 | 歷史安全Pod與現存設定 |
| [week20/day3-networkpolicy-tenant-isolation](<../../docs/week20/day3-networkpolicy-tenant-isolation.md>) | 已核對、頁首已修正 | 20260921隔離Calico驗收 |
| [week20/day4-ha-node-failure-recovery](<../../docs/week20/day4-ha-node-failure-recovery.md>) | 已核對、頁首已修正 | 歷史整組重建，非最終工作恢復 |
| [week20/day5-ai-hpc-production-troubleshooting](<../../docs/week20/day5-ai-hpc-production-troubleshooting.md>) | 已核對、頁首已修正 | 歷史Ray retry與Slurm VM已刪除 |
| [week20/day6-ai-hpc-platform-technology-selection](<../../docs/week20/day6-ai-hpc-platform-technology-selection.md>) | 已核對、頁首已修正 | 選型概念，未部署技術 |

逐篇詳細判斷、引用摘錄與程式版本 hashes 見 [JSON 清單](curriculum-content-audit.json)。
