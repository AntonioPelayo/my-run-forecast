from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import numpy as np

from gpx_time_prediction_models.training.features import build_training_matrix
from utils import activity as au
from utils.config import PARQUET_RUN_ACTIVITIES_PATH


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
    model_version: str
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
        "feature_stds": matrix.feature_stds.tolist(),
        "target_name": "elapsed_seconds",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)


def main() -> None:
    model_version = f"normalized_linear_v{datetime.now().strftime('%Y_%m_%d')}"
    input_data_path = PARQUET_RUN_ACTIVITIES_PATH
    output_path = Path(f"gpx_time_prediction_models/artifacts/{model_version}.json")
    train_and_save(input_data_path, output_path, model_version)


if __name__ == "__main__":
    main()
