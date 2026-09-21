# 以單程序或 DDP 訓練比較吞吐量；依 CUDA 可用性選擇 NCCL 或 Gloo。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import os
import time

import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.profiler import (
    ProfilerActivity,
    profile,
    schedule,
)
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.distributed import DistributedSampler


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    # torchrun provides distributed environment variables.
    # os.environ.get 讀取 torchrun 提供的環境變數；int 把字串轉成整數。
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    distributed = world_size > 1

    use_cuda = torch.cuda.is_available()

    if distributed:
        # 條件運算式 A if 條件 else B：GPU 選 NCCL，CPU 選 Gloo。
        backend = "nccl" if use_cuda else "gloo"
        # 初始化分散式通訊群組；torchrun 提供 rank、world size 與 rendezvous 環境。
        dist.init_process_group(backend=backend)

    rank = dist.get_rank() if distributed else 0

    if use_cuda:
        # 把本程序綁到 local_rank 對應的 GPU，避免同節點所有程序使用同一張卡。
        torch.cuda.set_device(local_rank)
        device = torch.device(f"cuda:{local_rank}")
    else:
        device = torch.device("cpu")

    backend = "nccl" if use_cuda else "gloo"

    print(
        f"INIT rank={rank} "
        f"world_size={world_size} "
        f"backend={backend} "
        f"device={device}"
    )

    #
    # Synthetic training workload
    #
    sample_count = 20000
    input_size = 1024
    batch_size = 512
    epochs = 20

    x = torch.randn(sample_count, input_size)
    y = torch.randn(sample_count, 1)

    dataset = TensorDataset(x, y)

    sampler = None

    if distributed:
        # 依 rank 切分資料；各 worker 讀取自己的份額。
        sampler = DistributedSampler(
            dataset,
            num_replicas=world_size,
            rank=rank,
            shuffle=True,
        )

    # 將資料集分成 mini-batch；shuffle 控制打亂，num_workers 控制載入子程序數。
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(sampler is None),
        sampler=sampler,
        num_workers=0,
    )

    #
    # Model
    #
    # Sequential 依序執行各層；Linear 轉換維度，ReLU 將負值截為零。
    model = nn.Sequential(
        nn.Linear(input_size, 4096),
        nn.ReLU(),
        nn.Linear(4096, 1),
    )

    model = model.to(device)

    if distributed:
        if use_cuda:
            model = DDP(
                model,
                device_ids=[local_rank],
            )
        else:
            model = DDP(model)

    # 隨機梯度下降最佳化器；lr 是每次參數更新的學習率。
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
    )

    # 均方誤差損失：衡量預測值與目標值的平方差。
    loss_fn = nn.MSELoss()

    #
    # Profiler
    #
    # Only rank 0 records profiler data.
    profiler = None

    # 只讓 rank 0 建立 profiler，減少多程序重複收集；這裡僅啟用 CPU activity。
    if rank == 0:
        profiler = profile(
            activities=[
                ProfilerActivity.CPU,
            ],
            schedule=schedule(
                wait=1,
                warmup=1,
                active=3,
            ),
            record_shapes=True,
            profile_memory=True,
        )

        profiler.start()

    #
    # Training benchmark
    #
    if use_cuda:
        # 等待非同步 CUDA 工作完成，確保後續計時包含 GPU 實際耗時。
        torch.cuda.synchronize()

    # 使用高解析度單調計時器量測經過時間。
    start_time = time.perf_counter()

    local_samples = 0

    for epoch in range(epochs):

        if sampler is not None:
            # 每個 epoch 更新 shuffle 種子，避免每輪都使用相同的分配順序。
            sampler.set_epoch(epoch)

        for inputs, targets in dataloader:

            inputs = inputs.to(device)
            targets = targets.to(device)

            # 清除上一批次累積的梯度，避免梯度意外相加。
            optimizer.zero_grad()

            outputs = model(inputs)

            loss = loss_fn(
                outputs,
                targets,
            )

            # DDP gradient synchronization happens here.
            # 反向傳播計算梯度；DDP 在這個階段同步各 rank 梯度。
            loss.backward()

            # 依梯度與學習率更新模型參數。
            optimizer.step()

            local_samples += inputs.size(0)

            if profiler is not None:
                profiler.step()

    if profiler is not None:
        profiler.stop()

    if use_cuda:
        # 等待非同步 CUDA 工作完成，確保後續計時包含 GPU 實際耗時。
        torch.cuda.synchronize()

    # 使用高解析度單調計時器量測經過時間。
    duration = time.perf_counter() - start_time

    #
    # Aggregate samples from all workers.
    #
    sample_tensor = torch.tensor(
        float(local_samples),
        device=device,
    )

    if distributed:
        # 跨 rank 歸約張量並讓每個 rank 取得結果；此操作會原地更新張量。
        dist.all_reduce(
            sample_tensor,
            op=dist.ReduceOp.SUM,
        )

    global_samples = int(sample_tensor.item())

    # 吞吐量是全體樣本數除以本程序量測時間；此處未取各 rank duration 的最大值。
    throughput = global_samples / duration

    #
    # Print profiler result.
    #
    if rank == 0 and profiler is not None:
        print(
            "\n=== PROFILER TOP CPU OPERATIONS ==="
        )

        print(
            profiler.key_averages()
            .table(
                sort_by="self_cpu_time_total",
                row_limit=20,
            )
        )

    #
    # Final scaling result.
    #
    if rank == 0:
        print(
            "\nSCALING_RESULT "
            f"backend={backend} "
            f"device={device.type} "
            f"workers={world_size} "
            f"samples={global_samples} "
            f"duration={duration:.3f}s "
            f"throughput={throughput:.2f}_samples_per_sec"
        )

    if distributed:
        # 釋放分散式通訊群組資源。
        dist.destroy_process_group()


# __name__ 在直接執行此檔時為 __main__；被 import 時不會執行這個入口。
if __name__ == "__main__":
    main()
