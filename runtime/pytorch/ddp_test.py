import os

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def main():
    # Initialize the distributed process group.
    # Gloo is used here because this lab runs DDP workers on CPU.
    dist.init_process_group(backend="gloo")

    # torchrun automatically provides these distributed environment values.
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    local_rank = int(os.environ["LOCAL_RANK"])

    # Create a simple model.
    # Each DDP worker owns its own model replica.
    model = torch.nn.Linear(4, 1)

    # Wrap the model with DistributedDataParallel.
    # DDP automatically synchronizes gradients during backward().
    model = DDP(model)

    # Create local input data for this worker.
    # Different workers may process different data,
    # so their local loss values do not need to be identical.
    x = torch.randn(8, 4)
    y = torch.randn(8, 1)

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
    )

    optimizer.zero_grad()

    # Forward pass on the local worker.
    output = model(x)
    loss = torch.nn.functional.mse_loss(output, y)

    # During backward(), DDP synchronizes gradients
    # across all workers through the process group.
    loss.backward()

    # Since gradients are synchronized, every worker performs
    # the optimizer step using equivalent gradients.
    optimizer.step()

    # Calculate a simple checksum of all model parameters.
    # If DDP synchronization works correctly, every worker
    # should have the same checksum after optimizer.step().
    with torch.no_grad():
        param_checksum = sum(
            parameter.sum().item()
            for parameter in model.parameters()
        )

    # Print distributed runtime information and validation evidence.
    print(
        f"RANK={rank} "
        f"LOCAL_RANK={local_rank} "
        f"WORLD_SIZE={world_size} "
        f"LOSS={loss.item():.6f} "
        f"PARAM_CHECKSUM={param_checksum:.6f}"
    )

    # Cleanly shut down the distributed process group.
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
