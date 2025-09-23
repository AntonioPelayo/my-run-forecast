from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from models import time_linear
from utils import activity

@dataclass
class TrainingConfig:
    hidden_sizes: tuple[int, ...] = (64, 32)
    dropout: float = 0.1
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 300
    batch_size: int = 32
    device: str = "cpu"


class TimeMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_sizes: Sequence[int], dropout: float) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = input_dim
        for size in hidden_sizes:
            layers.append(nn.Linear(prev, size))
            layers.append(nn.ReLU())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev = size
        layers.append(nn.Linear(prev, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x).squeeze(-1)


def _standardize(features: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = features.mean(axis=0)
    std = features.std(axis=0)
    std[std == 0] = 1.0
    normalized = (features - mean) / std
    return normalized, mean, std


def _build_dataloader(
    features: np.ndarray,
    targets: np.ndarray,
    batch_size: int,
    shuffle: bool = True,
) -> DataLoader:
    tensor_x = torch.from_numpy(features).float()
    tensor_y = torch.from_numpy(targets).float()
    dataset = TensorDataset(tensor_x, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_time_mlp(
    summaries_df,
    feature_names: Iterable[str] | None = None,
    config: TrainingConfig | None = None,
) -> tuple[TimeMLP, dict[str, np.ndarray], list[float]]:
    if config is None:
        config = TrainingConfig()

    if feature_names is None:
        feature_names = time_linear.LINEAR_FEATURES

    label_col = "elapsed_time_hours"
    feature_names = list(feature_names)

    frame = summaries_df[[label_col, *feature_names]].dropna()
    if frame.empty:
        raise ValueError("No complete rows available for training the torch model")

    features = frame[feature_names].to_numpy(dtype=np.float32)
    labels = frame[label_col].to_numpy(dtype=np.float32)

    normalized, mean, std = _standardize(features)

    device = torch.device(config.device)
    model = TimeMLP(input_dim=normalized.shape[1], hidden_sizes=config.hidden_sizes, dropout=config.dropout)
    model.to(device)

    loader = _build_dataloader(normalized, labels, config.batch_size)

    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    criterion = nn.MSELoss()

    history: list[float] = []
    for _ in range(config.epochs):
        epoch_loss = 0.0
        model.train()
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * batch_x.size(0)

        history.append(epoch_loss / len(loader.dataset))

    stats = {
        "feature_names": np.array(feature_names),
        "mean": mean,
        "std": std,
    }
    return model, stats, history


def save_model(model: TimeMLP, stats: dict[str, np.ndarray], path: Path) -> None:
    path = Path(path)
    payload = {
        "state_dict": model.state_dict(),
        "feature_names": list(stats["feature_names"]),
        "mean": stats["mean"].tolist(),
        "std": stats["std"].tolist(),
    }
    torch.save(payload, path)


def load_model(path: Path, device: str | None = None) -> tuple[TimeMLP, dict[str, np.ndarray]]:
    checkpoint = torch.load(Path(path), map_location=device or "cpu", weights_only=False)
    feature_names = checkpoint["feature_names"]
    mean = np.array(checkpoint["mean"], dtype=np.float32)
    std = np.array(checkpoint["std"], dtype=np.float32)

    model = TimeMLP(
        input_dim=len(feature_names),
        hidden_sizes=TrainingConfig().hidden_sizes,
        dropout=TrainingConfig().dropout,
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, {"feature_names": np.array(feature_names), "mean": mean, "std": std}


def predict_hours(model: TimeMLP, stats: dict[str, np.ndarray], features: dict[str, float]) -> float:
    feature_names = stats["feature_names"]
    values = np.array([features[name] for name in feature_names], dtype=np.float32)
    normalized = (values - stats["mean"]) / stats["std"]
    with torch.no_grad():
        tensor = torch.from_numpy(normalized).float().unsqueeze(0)
        prediction = model(tensor).item()
    return float(prediction)


def plot_training_loss(history: Sequence[float]) -> None:
    import matplotlib.pyplot as plt

    plt.plot(history)
    plt.xlabel("Epoch")
    plt.ylabel("Training Loss (MSE)")
    plt.title("Training Loss over Epochs")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


def main() -> None:
    ACTIVITY_DIR = Path('./data/parquet_run_activities')
    WEIGHTS_PATH = Path('./models/weights/time_mlp_weights.pt')

    summaries = activity.load_activity_summaries(ACTIVITY_DIR)
    config = TrainingConfig(epochs=400, batch_size=32, lr=5e-4, dropout=0.1)
    model, stats, history = train_time_mlp(summaries, config=config)

    save_model(model, stats, WEIGHTS_PATH)
    plot_training_loss(history)


if __name__ == '__main__':
    main()
