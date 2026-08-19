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


def main():
    # torchrun provides distributed environment variables.
    world_size = int(os.environ.get("WORLD_SIZE", "1"))
    local_rank = int(os.environ.get("LOCAL_RANK", "0"))

    distributed = world_size > 1

    use_cuda = torch.cuda.is_available()

    if distributed:
        backend = "nccl" if use_cuda else "gloo"
        dist.init_process_group(backend=backend)

    rank = dist.get_rank() if distributed else 0

    if use_cuda:
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
        sampler = DistributedSampler(
            dataset,
            num_replicas=world_size,
            rank=rank,
            shuffle=True,
        )

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

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
    )

    loss_fn = nn.MSELoss()

    #
    # Profiler
    #
    # Only rank 0 records profiler data.
    profiler = None

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
        torch.cuda.synchronize()

    start_time = time.perf_counter()

    local_samples = 0

    for epoch in range(epochs):

        if sampler is not None:
            sampler.set_epoch(epoch)

        for inputs, targets in dataloader:

            inputs = inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()

            outputs = model(inputs)

            loss = loss_fn(
                outputs,
                targets,
            )

            # DDP gradient synchronization happens here.
            loss.backward()

            optimizer.step()

            local_samples += inputs.size(0)

            if profiler is not None:
                profiler.step()

    if profiler is not None:
        profiler.stop()

    if use_cuda:
        torch.cuda.synchronize()

    duration = time.perf_counter() - start_time

    #
    # Aggregate samples from all workers.
    #
    sample_tensor = torch.tensor(
        float(local_samples),
        device=device,
    )

    if distributed:
        dist.all_reduce(
            sample_tensor,
            op=dist.ReduceOp.SUM,
        )

    global_samples = int(sample_tensor.item())

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
        dist.destroy_process_group()


if __name__ == "__main__":
    main()
