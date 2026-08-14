import torch
from torch.utils.data import DataLoader, TensorDataset


class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # Expand 1024 input features into a larger hidden representation
        self.layer1 = torch.nn.Linear(1024, 4096)
        # Convert the hidden representation into one prediction
        self.layer2 = torch.nn.Linear(4096, 1)


    def forward(self, x):
        # First linear transformation
        x = self.layer1(x)

        # Apply a non-linear activation
        x = torch.relu(x)

        # Produce the final prediction
        return self.layer2(x)

def main():
    # Verify that CUDA is available
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    # Select the first available CUDA GPU
    device = torch.device("cuda:0")

    # Create synthetic input data on CPU
    features = torch.randn(20000, 1024)

    # Create labels with a learnable relationship to the input features
    labels = features.sum(dim=1, keepdim=True)

    # Combine inputs and targets into one dataset
    dataset = TensorDataset(features, labels)

    # Create batches from the dataset
    dataloader = DataLoader(
        dataset,
        batch_size=512,
        shuffle=True,
    )

    # Create the model and move its parameters to GPU
    model = SimpleModel().to(device)

    # Create the loss function
    loss_function = torch.nn.MSELoss()

    # Create an optimizer for the model parameters
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=0.01,
    )

    # Set the number of training epochs
    epochs = 100

    print(f"Training Device: {device}")
    print(f"GPU: {torch.cuda.get_device_name(device)}")
    print(f"Dataset Size: {len(dataset)}")
    print(f"Batches Per Epoch: {len(dataloader)}")

    # Train the model for multiple epochs
    for epoch in range(epochs):
        epoch_loss = 0.0
        # Train all batches in the dataloader
        for features_batch, labels_batch in dataloader:

            # Move the current batch to GPU
            features_batch = features_batch.to(device)
            labels_batch = labels_batch.to(device)

            # Clear gradients from the previous batch
            optimizer.zero_grad()

            # Forward pass
            predictions = model(features_batch)

            # Calculate loss
            loss = loss_function(predictions, labels_batch)
            # Stop training if the loss becomes NaN or infinite
            if not torch.isfinite(loss):
                raise RuntimeError(
                    f"Non-finite loss detected: "
                    f"epoch={epoch + 1}, "
                    f"loss={loss.item()}"
            )


            # Calculate gradients
            loss.backward()

            # Update model parameters
            optimizer.step()

            # Accumulate batch loss
            epoch_loss += loss.item()

            # Calculate the average loss for this epoch
        average_loss = epoch_loss / len(dataloader)

        print(
            f"Epoch [{epoch + 1}/{epochs}] "
            f"Average Loss: {average_loss:.6f}"
        )

if __name__ == "__main__":
    main()
