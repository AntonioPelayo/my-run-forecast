from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

import numpy as np

from gpx_time_prediction_models.training.features import (
    FeatureMatrix,
    build_training_matrix
)
from utils import activity as au
from utils.config import PARQUET_RUN_ACTIVITIES_PATH


def fit_linear_regression(X: np.ndarray, y: np.ndarray) -> tuple[float, np.ndarray]:
    # Solve y = b0 + Xw using least squares.
    X_design = np.column_stack([np.ones(len(X)), X])
    coeffs, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    intercept = float(coeffs[0])
    weights = coeffs[1:].astype(float, copy=False)
    return intercept, weights


def train(training_matrix: FeatureMatrix, model_version: str) -> dict:
    intercept, coefficients = fit_linear_regression(
        training_matrix.X, training_matrix.y
    )

    artifact = {
        "model_version": model_version,
        "intercept": intercept,
        "coefficients": coefficients.tolist(),
        "feature_names": list(training_matrix.feature_names),
        "feature_means": training_matrix.feature_means.tolist(),
        "feature_stds": training_matrix.feature_stds.tolist(),
        "target_name": "elapsed_seconds",
    }
    return artifact


def save(
    artifact: dict,
    output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)


def main() -> None:
    output_path = Path("gpx_time_prediction_models/artifacts/")
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    model_version = f"linear_v{timestamp}"

    weights_file_name = "linear_weights.json"

    activity_summaries_df = au.activities_summary(PARQUET_RUN_ACTIVITIES_PATH)
    matrix = build_training_matrix(activity_summaries_df)

    artifact = train(matrix, model_version)
    save(artifact, output_path / weights_file_name)
    save(artifact, output_path / "backups" / f"{model_version}.json")


if __name__ == "__main__":
    main()
