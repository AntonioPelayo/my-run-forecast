from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gpx_time_prediction_models.training.features import build_training_matrix
from utils import activity as au


def fit_linear_regression(X: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray]:
    # Solve y = b0 + Xw using least squares.
    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    intercept = float(coeffs[0])
    weights = coeffs[1:].astype(float, copy=False)
    return intercept, weights


def train_and_save(
    input_data_path: Path,
    output_path: Path,
    model_version: str = "linear_v1",
) -> None:
    activity_summaries_df = au.activities_summary(input_data_path)
    matrix = build_training_matrix(activity_summaries_df)

    intercept, coefficients = fit_linear_regression(matrix.X, matrix.y)

    artifact = {
        "model_version": model_version,
        "intercept": intercept,
        "coefficients": coefficients.tolist(),
        "feature_names": list(matrix.feature_names),
        "feature_means": matrix.feature_means.tolist(),
        "target_name": "elapsed_seconds",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)


def main() -> None:
    input_data_path = Path("data/parquet_run_activities")
    output_path = Path("gpx_time_prediction_models/artifacts/linear_v1.json")
    train_and_save(input_data_path, output_path)


if __name__ == "__main__":
    main()
