# Week17 Day4 — Slurm Multi-node HPC Cluster

## 今日平台新增能力

今天從單機 Slurm Lab 升級成真正的 Multi-node HPC Cluster。

完成：

- Slurm Controller / Compute Node 架構
- MUNGE Multi-node Authentication
- Multi-node Partition
- Slurm Job / Task / Resource Allocation
- RUNNING / PENDING Queue 行為
- Multi-node Slurm Job
- Multi-node MPI Launch
- Open MPI 與 Slurm PMI 相容性問題分析
- HPC Cluster Shared Filesystem Limitation

---

## 1. Slurm 在 HPC 的角色

Slurm 主要負責：

- Job Scheduling
- CPU / GPU Resource Allocation
- Queue Management
- Node Management
- Partition Management

基本架構：

    User
      |
      v
    sbatch
      |
      v
    slurmctld
      |
      v
    Compute Nodes
      |
      v
    srun / mpirun
      |
      v
    MPI / PyTorch / NCCL Workload

Slurm 不負責 MPI Communication。

分工：

    Slurm
    = 決定 Job 何時跑、在哪些 Node 跑、分多少資源

    MPI
    = Process 之間的 Distributed Communication

    NCCL
    = NVIDIA GPU Collective Communication

---

## 2. Job / Task / srun

Job：

    提交給 Slurm 的整份工作。

例如：

    sbatch hello.slurm

Slurm 會產生：

    Job ID

Task：

    Job 裡面的執行單位，通常對應 Process。

例如：

    --ntasks=4

代表 Job 要啟動 4 個 Task。

srun：

    在 Slurm Allocation 中啟動 Task。

例如：

    srun hostname

若配置：

    --ntasks=2

則會啟動兩個 Task 執行 hostname。

---

## 3. CPU Resource Request

常見設定：

    #SBATCH --nodes=1
    #SBATCH --ntasks=4
    #SBATCH --cpus-per-task=2
    #SBATCH --mem=8G

代表：

    1 Node
    4 Tasks
    2 CPUs per Task
    8 GB Memory

總 CPU Requirement：

    4 Tasks × 2 CPUs
    = 8 CPUs

Task 不等於 CPU。

    Task
    = Process / Execution Unit

    CPU
    = 分配給 Task 使用的 Compute Resource

---

## 4. GPU Resource Request

GPU Job 的 Slurm 使用方式與 CPU Job 基本流程相同，只是增加 GPU Resource Request。

例如：

    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --gres=gpu:1

代表：

    1 Node
    1 Task
    1 GPU

典型 AI Job：

    sbatch
      |
      v
    Slurm Scheduler
      |
      v
    GPU Allocation
      |
      v
    srun / torchrun
      |
      v
    PyTorch Training

Multi-node GPU Job 可能配置：

    #SBATCH --nodes=2
    #SBATCH --ntasks-per-node=4
    #SBATCH --gres=gpu:4

代表：

    2 Nodes
    4 Tasks per Node
    4 GPUs per Node

---

## 5. Single-node Slurm Baseline

hpc-demo 硬體：

    CPUs=4
    RealMemory=15990 MB

使用：

    slurmd -C

得到：

    NodeName=hpc-demo
    CPUs=4
    Boards=1
    SocketsPerBoard=1
    CoresPerSocket=2
    ThreadsPerCore=2

最初建立：

    PartitionName=debug

並成功啟動：

    slurmctld
    slurmd

驗證：

    sinfo

結果：

    debug* up infinite 1 idle hpc-demo

---

## 6. Slurm cgroup 問題

最初設定：

    ProctrackType=proctrack/cgroup

slurmd 啟動失敗：

    cgroup namespace 'freezer' not mounted
    unable to create freezer cgroup namespace
    Couldn't load proctrack/cgroup

原因：

    Ubuntu 22.04 + Slurm 21.08
    與目前 cgroup environment 不相容。

Lab Workaround：

    ProctrackType=proctrack/linuxproc

linuxproc 透過 Linux /proc 追蹤 Job Process。

修改後：

    slurmd = active

Node：

    State=IDLE

正式 Production Environment 應使用：

    Newer Slurm
    +
    Correct cgroup v2 Configuration

本次 linuxproc 僅作為 Lab 相容性方案。

---

## 7. Queue / Resource Scheduling

建立：

    cpu-hold.slurm

使用：

    --ntasks=4

第一個 Job：

    RUNNING

第二個相同 Job：

    PENDING

實測：

    Job 3 -> R
    Job 4 -> PD (Resources)

原因：

    hpc-demo total CPU = 4

    Job 3 已配置全部 CPU

    Job 4 無足夠 Resource

因此進入：

    PENDING

這驗證了 Slurm：

    Resource Allocation
    +
    Queue Scheduling

---

## 8. Multi-node HPC Cluster 建立

使用 gcloud 建立：

    compute-01
    compute-02

規格：

    e2-medium
    2 vCPU
    4 GB RAM
    Ubuntu 22.04 LTS
    20 GB Disk

Network：

    Zone: asia-east1-a
    VPC: default
    Subnet: default

Internal IP：

    compute-01 = 10.140.0.7
    compute-02 = 10.140.0.8

---

## 9. Multi-node Software Environment

三台使用一致版本：

    Slurm 21.08.5
    Open MPI 4.1.2
    Ubuntu 22.04

架構：

    hpc-demo
    └── slurmctld

    compute-01
    └── slurmd

    compute-02
    └── slurmd

---

## 10. MUNGE Authentication

Slurm Multi-node Cluster 需要所有 Node 使用相同：

    /etc/munge/munge.key

架構：

    hpc-demo
        |
        +--> compute-01
        |
        +--> compute-02

MUNGE 用於：

    Slurm Controller
        |
        v
    Authenticated Credential
        |
        v
    Compute Node

Key 不一致會導致：

    Node Registration Failure
    Job Launch Failure
    Authentication Failure

---

## 11. Multi-node slurm.conf

Compute Node 規格：

    compute-01
    CPUs=2
    RealMemory=3800

    compute-02
    CPUs=2
    RealMemory=3800

建立 Partition：

    PartitionName=cpu
    Nodes=compute-01,compute-02
    Default=YES
    State=UP

Controller：

    hpc-demo

Compute Nodes：

    compute-01
    compute-02

hpc-demo 不再執行 slurmd，只作為 Controller / Login Node。

---

## 12. Multi-node Cluster 驗證

執行：

    sinfo

結果：

    PARTITION AVAIL TIMELIMIT NODES STATE NODELIST
    cpu*         up   infinite    2 idle  compute-[01-02]

執行：

    scontrol show nodes

確認：

    compute-01
    State=IDLE
    CPUTot=2
    RealMemory=3800

    compute-02
    State=IDLE
    CPUTot=2
    RealMemory=3800

代表：

    Slurm Controller 已正常管理兩個 Compute Nodes。

---

## 13. Multi-node Slurm Job

Job Request：

    #SBATCH --nodes=2
    #SBATCH --ntasks-per-node=2

代表：

    2 Nodes
    ×
    2 Tasks per Node
    =
    4 Tasks

使用：

    srun hostname

實測：

    JOB_ID=6
    NODELIST=compute-[01-02]
    NTASKS=4

    compute-02
    compute-01
    compute-02
    compute-01

證明：

    一個 Slurm Job
        |
        v
    2 Compute Nodes
        |
        v
    4 Tasks
        |
        v
    Cross-node Execution

---

## 14. Shared Filesystem 問題

第一次 Multi-node Job 失敗：

    WEXITSTATUS 1

原因：

Job 從：

    /root/hpc-ai-benchmark-platform

提交。

但：

    compute-01
    compute-02

並沒有相同 Working Directory。

修正：

    #SBATCH --chdir=/tmp
    #SBATCH --output=/tmp/multi-node-%j.out

這揭露真正 HPC Cluster 的重要需求：

    Compute
    +
    Scheduler
    +
    Network
    +
    Shared Storage

正式 HPC 常使用：

- NFS
- Lustre
- BeeGFS
- GPFS / Spectrum Scale
- Parallel Filesystem

本次 Lab 未部署 Shared Filesystem。

---

## 15. Slurm + MPI Integration

Slurm 支援：

    srun --mpi=list

本次結果：

    pmi2
    none
    cray_shasta

嘗試：

    srun --mpi=pmi2

失敗：

    OMPI was not built with SLURM's PMI support

原因：

Slurm 有 PMI2 Plugin，但 Ubuntu 套件版：

    Open MPI 4.1.2

沒有編譯對應的 Slurm PMI Support。

因此：

    srun direct MPI launch
    = unavailable

本次採用：

    Slurm
    = Resource Allocation

    Open MPI mpirun
    = MPI Rank Launch

---

## 16. Worker-to-worker SSH

Open MPI 使用 mpirun 跨 Node 啟動 Process，因此建立：

    compute-01 -> compute-02

以及：

    compute-02 -> compute-01

Passwordless SSH。

驗證：

    ssh compute-02 hostname

結果：

    compute-02

反方向：

    ssh compute-01 hostname

結果：

    compute-01

---

## 17. Multi-node MPI Execution

Slurm Job：

    #SBATCH --nodes=2
    #SBATCH --ntasks-per-node=2

MPI：

    mpirun \
      --allow-run-as-root \
      --host compute-01:2,compute-02:2 \
      -np 4 \
      /tmp/mpi_hello

最終實測：

    JOB_ID=14
    NODELIST=compute-[01-02]
    NTASKS=4

    Hello from rank 0 out of 4 processes
    Hello from rank 1 out of 4 processes
    Hello from rank 3 out of 4 processes
    Hello from rank 2 out of 4 processes

架構：

    hpc-demo
    slurmctld
        |
        +----------------------+
        |                      |
    compute-01             compute-02
      slurmd                  slurmd
      MPI Ranks               MPI Ranks
        \                      /
         \------ MPI/TCP -----/

這證明：

    Slurm Multi-node Scheduling
    +
    Open MPI Multi-node Launch
    +
    Cross-node MPI Communication

均已成功。

---

## 18. OSU Multi-node Benchmark

原計畫：

    Single-node OMB
        vs
    Multi-node OMB

比較：

- Latency
- Bandwidth
- Shared Memory vs Ethernet

嘗試在 compute node 編譯：

    OSU Micro-Benchmarks 7.5.2

但 configure 遇到：

    C++ preprocessor "/lib/cpp" fails sanity check

因此本日未繼續修復。

目前已有 Day2 Single-node Baseline：

    osu_latency
    1 B ≈ 0.43 us

    osu_bw
    Peak ≈ 8.36 GB/s

Multi-node OMB：

    Not validated today

不可宣稱 Multi-node Latency / Bandwidth Result。

---

## 19. 最終 HPC Cluster Architecture

本日完成架構：

    hpc-demo
    Login / Controller
    slurmctld
          |
          |
    -------------------------
    |                       |
    v                       v
    compute-01              compute-02
    slurmd                  slurmd
    2 vCPU                  2 vCPU
    3.8 GB RAM              3.8 GB RAM
       \                       /
        \                     /
         ------ MPI/TCP ------
                 |
                 v
        Distributed Workload

這是一個真正可排程與執行 Multi-node MPI Workload 的 CPU HPC Lab Cluster。

---

## 今日成果

完成：

- Slurm Job / Task / srun 概念
- Partition / Queue / Resource Scheduling
- RUNNING / PENDING 行為
- Slurm cgroup Compatibility Troubleshooting
- 建立 2 台 GCP Compute Nodes
- Multi-node MUNGE Authentication
- Multi-node Slurm Configuration
- Controller / Compute Node Role Separation
- Multi-node Job Scheduling
- Cross-node Task Execution
- Shared Filesystem Limitation Analysis
- Slurm PMI / Open MPI Compatibility Analysis
- Worker-to-worker SSH
- Slurm + Open MPI Multi-node Execution

目前正式能力：

    hpc-demo
       |
       v
    Slurm Scheduler
       |
       v
    compute-01 + compute-02
       |
       v
    Multi-node MPI Workload

本日 Multi-node OSU Benchmark 因 Build Environment 問題未完成，不宣稱不存在的 Performance Result。

---

## Interview Review

### Q1：Slurm 與 MPI 在 HPC Cluster 中分別負責什麼？

Slurm 負責 Job Queue、Node 與 CPU/GPU Resource Allocation，以及決定 Workload 在何時、哪些 Compute Nodes 上執行。

MPI 則負責不同 Process / Node 之間的 Distributed Communication。

### Q2：為什麼 Multi-node HPC Cluster 通常需要 Shared Filesystem？

因為每台 Compute Node 都有自己的 Local Filesystem。若程式、Input Data 或 Output Path 只存在 Login Node，Compute Node 可能無法存取，導致 Job 啟動或執行失敗。Shared Filesystem 可讓所有 Nodes 使用一致的程式與資料路徑。
