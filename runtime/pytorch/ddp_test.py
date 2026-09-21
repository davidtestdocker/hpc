# CPU／Gloo DDP 實驗：各程序持有模型副本，在反向傳播時同步梯度。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import os

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    # Initialize the distributed process group.
    # Gloo is used here because this lab runs DDP workers on CPU.
    # 初始化分散式通訊群組；torchrun 提供 rank、world size 與 rendezvous 環境。
    dist.init_process_group(backend="gloo")

    # torchrun automatically provides these distributed environment values.
    # rank 是全群組程序編號，world_size 是程序總數，local_rank 是本節點內編號。
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    local_rank = int(os.environ["LOCAL_RANK"])

    # Create a simple model.
    # Each DDP worker owns its own model replica.
    # 線性層把輸入特徵轉為指定輸出維度，包含可訓練權重與偏差。
    model = torch.nn.Linear(4, 1)

    # Wrap the model with DistributedDataParallel.
    # DDP automatically synchronizes gradients during backward().
    # DDP 包装本機模型副本，初始化時同步參數，backward 時同步梯度。
    model = DDP(model)

    # Create local input data for this worker.
    # Different workers may process different data,
    # so their local loss values do not need to be identical.
    # randn 產生標準常態隨機張量；此處每個 worker 各自產生 8 筆、每筆 4 個特徵。
    x = torch.randn(8, 4)
    y = torch.randn(8, 1)

    # 隨機梯度下降最佳化器；lr 是每次參數更新的學習率。
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
    )

    # 清除上一批次累積的梯度，避免梯度意外相加。
    optimizer.zero_grad()

    # Forward pass on the local worker.
    output = model(x)
    loss = torch.nn.functional.mse_loss(output, y)

    # During backward(), DDP synchronizes gradients
    # across all workers through the process group.
    # 反向傳播計算梯度；DDP 在這個階段同步各 rank 梯度。
    loss.backward()

    # Since gradients are synchronized, every worker performs
    # the optimizer step using equivalent gradients.
    # 依梯度與學習率更新模型參數。
    optimizer.step()

    # Calculate a simple checksum of all model parameters.
    # If DDP synchronization works correctly, every worker
    # should have the same checksum after optimizer.step().
    # 停用梯度追蹤以檢查參數；生成式逐個參數求和，item 將單值張量轉成 Python 數值。
    # 各 rank 的加總一致是簡易檢查，並非逐元素相等的完整證明。
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
    # 釋放分散式通訊群組資源。
    dist.destroy_process_group()


# __name__ 在直接執行此檔時為 __main__；被 import 時不會執行這個入口。
if __name__ == "__main__":
    main()
