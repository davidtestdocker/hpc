# 以合成資料執行 GPU 訓練，使用 profiler 觀察 CPU／CUDA 操作耗時。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import torch
from torch.utils.data import DataLoader, TensorDataset
from torch.profiler import profile, ProfilerActivity, schedule


# class 定義 SimpleModel 類別；括號內是繼承的父類別。
class SimpleModel(torch.nn.Module):
    # 建構子：建立實例時初始化狀態；self 代表此物件本身。
    def __init__(self):
        super().__init__()

        # Expand 1024 input features into a larger hidden representation
        # 線性層把輸入特徵轉為指定輸出維度，包含可訓練權重與偏差。
        self.layer1 = torch.nn.Linear(1024, 4096)

        # Convert the hidden representation into one prediction
        # 線性層把輸入特徵轉為指定輸出維度，包含可訓練權重與偏差。
        self.layer2 = torch.nn.Linear(4096, 1)

    # 定義模型前向計算，PyTorch 呼叫模型時會使用此方法。
    def forward(self, x):
        # First linear transformation
        x = self.layer1(x)

        # Apply a non-linear activation
        # ReLU 逐元素取 max(0, x)，為模型加入非線性。
        x = torch.relu(x)

        # Produce the final prediction
        return self.layer2(x)


# 程式主要流程；檔案直接執行時由最下方入口呼叫。
def main():
    # Verify that CUDA is available
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    # Select the first available CUDA GPU
    device = torch.device("cuda:0")

    # Create synthetic input data on CPU
    features = torch.randn(20000, 1024)

    # Create labels with a learnable relationship to the input features
    # dim=1 沿特徵維度加總；keepdim=True 保留維度，讓目標形狀符合模型輸出。
    labels = features.sum(dim=1, keepdim=True)

    # Combine inputs and targets into one dataset
    dataset = TensorDataset(features, labels)

    # Create batches from the dataset
    # 將資料集分成 mini-batch；shuffle 控制打亂，num_workers 控制載入子程序數。
    dataloader = DataLoader(
        dataset,
        batch_size=512,
        shuffle=True,
        num_workers=2,
    )

    # Create the model and move its parameters to GPU
    # to(device) 把模型參數移到 GPU；每批輸入也必須移到同一裝置。
    model = SimpleModel().to(device)

    # Create the loss function
    # 均方誤差損失：衡量預測值與目標值的平方差。
    loss_function = torch.nn.MSELoss()

    # Create an optimizer for the model parameters
    # 隨機梯度下降最佳化器；lr 是每次參數更新的學習率。
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.001,
    )

    # Configure profiler phases
    # schedule 分成等待 2 步、預熱 2 步、記錄 5 步；repeat=1 只收集一輪。
    profiler_schedule = schedule(
        wait=2,
        warmup=2,
        active=5,
        repeat=1,
    )

    # Total steps required by the profiler schedule
    total_steps = 9

    print(f"Training Device: {device}")
    print(f"GPU: {torch.cuda.get_device_name(device)}")
    print(f"Dataset Size: {len(dataset)}")
    print(f"Batches Per Epoch: {len(dataloader)}")
    # 將資料集分成 mini-batch；shuffle 控制打亂，num_workers 控制載入子程序數。
    print(f"DataLoader Workers: {dataloader.num_workers}")
    print(f"Profiler Total Steps: {total_steps}")

    # Profile representative steady-state training steps
    # with 管理 profiler 開始與結束；record_shapes 記錄張量形狀，profile_memory 記錄記憶體。
    with profile(
        activities=[
            ProfilerActivity.CPU,
            ProfilerActivity.CUDA,
        ],
        schedule=profiler_schedule,
        record_shapes=True,
        profile_memory=True,
    ) as prof:

        completed_steps = 0

        for features_batch, labels_batch in dataloader:
            # Move the current batch to GPU
            features_batch = features_batch.to(device)
            labels_batch = labels_batch.to(device)

            # Clear gradients from the previous batch
            # 清除上一批次累積的梯度，避免梯度意外相加。
            optimizer.zero_grad()

            # Forward pass
            predictions = model(features_batch)

            # Calculate loss
            loss = loss_function(predictions, labels_batch)

            # Stop training if the loss becomes NaN or infinite
            # isfinite 檢查是否為有限值；NaN 或無限大代表數值已不適合繼續訓練。
            if not torch.isfinite(loss):
                raise RuntimeError(
                    f"Non-finite loss detected: loss={loss.item()}"
                )

            # Calculate gradients
            # 反向傳播計算梯度；DDP 在這個階段同步各 rank 梯度。
            loss.backward()

            # Update model parameters
            # 依梯度與學習率更新模型參數。
            optimizer.step()

            # Mark one training step as completed
            # 通知 profiler 一個訓練步驟結束，用以推進 schedule。
            prof.step()

            completed_steps += 1

            if completed_steps >= total_steps:
                break

    print("\n=== PyTorch Profiler: CUDA Time ===")

    print(
        prof.key_averages().table(
            sort_by="cuda_time_total",
            row_limit=20,
        )
    )


    print("\n=== PyTorch Profiler: CPU Time ===")

    print(
        prof.key_averages().table(
            sort_by="cpu_time_total",
            row_limit=20,
        )
    )


# __name__ 在直接執行此檔時為 __main__；被 import 時不會執行這個入口。
if __name__ == "__main__":
    main()
