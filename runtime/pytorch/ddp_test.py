import os

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def main():
    dist.init_process_group(backend="gloo")

    rank = dist.get_rank()
    world_size = dist.get_world_size()
    local_rank = int(os.environ["LOCAL_RANK"])

    model = torch.nn.Linear(4, 1)
    model = DDP(model)

    x = torch.randn(8, 4)
    y = torch.randn(8, 1)

    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    optimizer.zero_grad()

    output = model(x)
    loss = torch.nn.functional.mse_loss(output, y)

    loss.backward()
    optimizer.step()

    print(
        f"RANK={rank} "
        f"LOCAL_RANK={local_rank} "
        f"WORLD_SIZE={world_size} "
        f"LOSS={loss.item():.6f}"
    )

    dist.destroy_process_group()


if __name__ == "__main__":
    main()
