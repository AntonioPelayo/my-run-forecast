from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from utils import activity

LINEAR_FEATURES: tuple[str, ...] = (
    "distance_mi",
    "elevation_gain_ft",
    "average_hr",
    "avg_cadence",
    "avg_power",
)


@dataclass(frozen=True)
class LinearTimeModel:
    intercept: float
    coefficients: np.ndarray
    feature_names: tuple[str, ...]
    feature_means: np.ndarray

    def predict_hours(self, features: dict[str, float]) -> float:
        vector = np.array([features[name] for name in self.feature_names], dtype=float)
        return float(self.intercept + vector @ self.coefficients)

    def to_series(self) -> pd.Series:
        return pd.Series(
            {
                "intercept": self.intercept,
                **{f"coef_{name}": coef for name, coef in zip(self.feature_names, self.coefficients)},
            }
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "intercept": self.intercept,
            "coefficients": self.coefficients.tolist(),
            "feature_names": list(self.feature_names),
            "feature_means": self.feature_means.tolist(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "LinearTimeModel":
        return cls(
            intercept=float(payload["intercept"]),
            coefficients=np.asarray(payload["coefficients"], dtype=float),
            feature_names=tuple(payload["feature_names"]),
            feature_means=np.asarray(payload["feature_means"], dtype=float),
        )


def train_linear_time_model(summaries: pd.DataFrame) -> LinearTimeModel:
    required_cols = ("elapsed_time_hours",) + LINEAR_FEATURES
    missing = [col for col in required_cols if col not in summaries.columns]
    if missing:
        raise ValueError(f"Missing columns for linear model: {missing}")

    training_df = summaries[list(required_cols)].dropna()
    if training_df.empty:
        raise ValueError("No complete activity rows to train linear model")

    X = training_df[list(LINEAR_FEATURES)].to_numpy(dtype=float)
    y = training_df["elapsed_time_hours"].to_numpy(dtype=float)

    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)

    intercept = float(coeffs[0])
    weights = coeffs[1:]
    feature_means = training_df[list(LINEAR_FEATURES)].mean().to_numpy(dtype=float)

    return LinearTimeModel(
        intercept=intercept,
        coefficients=weights.astype(float, copy=False),
        feature_names=LINEAR_FEATURES,
        feature_means=feature_means,
    )


def load_model(path: Path) -> LinearTimeModel:
    payload = pd.read_json(path, typ="series")
    return LinearTimeModel.from_dict(payload.to_dict())


def save_model(model: LinearTimeModel, path: Path) -> None:
    series = pd.Series(model.to_dict())
    series.to_json(path)

def main() -> None:
    ACTIVITY_DIR = Path('./data/parquet_run_activities')
    WEIGHTS_PATH = Path('./models/weights/time_linear_weights.json')

    summaries = activity.load_activity_summaries(ACTIVITY_DIR)
    model = train_linear_time_model(summaries)
    save_model(model, WEIGHTS_PATH)

if __name__ == '__main__':
    main()
