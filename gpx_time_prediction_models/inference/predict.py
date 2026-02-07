from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gpx_time_prediction_models.training.features import build_inference_vector
from utils import gpx as gu
from utils import time as tu

def load_artifact(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        artifact = json.load(f)

    required = ("intercept", "coefficients", "feature_names", "model_version")
    missing = [k for k in required if k not in artifact]
    if missing:
        raise ValueError(f"Artifact missing keys: {missing}")

    return artifact


def predict_elapsed_seconds(
    artifact: dict,
    distance: float,
    cum_altitude_gain: float,
    is_trail: bool,
) -> float:
    features = build_inference_vector(
        distance=distance,
        cum_altitude_gain=cum_altitude_gain,
        is_trail=is_trail,
    )

    feature_names = artifact["feature_names"]
    vector = np.array([features[name] for name in feature_names], dtype=float)

    intercept = float(artifact["intercept"])
    coefficients = np.array(artifact["coefficients"], dtype=float)

    if len(coefficients) != len(vector):
        raise ValueError(
            f"Coefficient length {len(coefficients)} != feature length {len(vector)}"
        )

    pred = intercept + float(vector @ coefficients)
    return max(0.0, pred)


def main() -> None:
    artifact_path = Path("gpx_time_prediction_models/artifacts/linear_v1.json")
    artifact = load_artifact(artifact_path)
    gpx_path = Path("data/gpx_routes/tower_oab.gpx")
    distance, cum_altitude_gain = gu.route_summary(gpx_path)

    seconds = predict_elapsed_seconds(
        artifact=artifact,
        distance=distance,
        cum_altitude_gain=cum_altitude_gain,
        is_trail=False
    )
    print(f"Predicted elapsed_seconds: {seconds:.1f}")

    hours = tu.seconds_to_hours(seconds)
    print(f"Predicted elapsed time: {tu.hours_to_hhmmss(hours)}")
    hhmmss = tu.hours_to_hhmmss(hours)
    print(f"Predicted elapsed time (hh:mm:ss): {hhmmss}")


if __name__ == "__main__":
    main()
