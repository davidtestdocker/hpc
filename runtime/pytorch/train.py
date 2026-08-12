import torch
from torch.utils.data import DataLoader, TensorDataset


class SimpleModel(torch.nn.Module):
    def __init__(self):
        super().__init__()

        # Map 10 input features to 1 prediction
        self.linear = torch.nn.Linear(10, 1)

    def forward(self, x):
        # Run input data through the linear layer
        return self.linear(x)


def main():
    # Verify that CUDA is available
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    # Select the first available CUDA GPU
    device = torch.device("cuda:0")

    # Create synthetic input data on CPU
    features = torch.randn(1000, 10)

    # Create labels with a learnable relationship to the input features
    labels = features.sum(dim=1, keepdim=True)

    # Combine inputs and targets into one dataset
    dataset = TensorDataset(features, labels)

    # Create batches from the dataset
    dataloader = DataLoader(
        dataset,
        batch_size=64,
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
