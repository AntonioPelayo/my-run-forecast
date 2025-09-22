from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd

from config import (
    DISTANCE_M_COL,
    ELAPSED_TIME_S_COL,
    MPS_TO_MPH_MULTIPLIER,
)
from models import pace as pace_models
from models import time_linear, time_torch
from utils import gpx as gpxu
from utils.time import hours_to_hhmmss


@dataclass(frozen=True)
class PaceModel:
    """Callable that reduces a workout to an average speed (m/s)."""

    name: str
    func: Callable[[pd.Series, pd.Series], float]
    description: str = ""


PACE_MODELS: tuple[PaceModel, ...] = (
    PaceModel(
        name="avg_speed_basic",
        func=pace_models.avg_speed_basic,
        description="distance delta / elapsed delta",
    ),
    PaceModel(
        name="avg_speed_weighted",
        func=pace_models.avg_speed_weighted,
        description="mean of per-sample instantaneous speeds",
    ),
)

DEFAULT_LINEAR_MODEL_PATH = Path("models/time_linear_weights.json")
DEFAULT_TORCH_MODEL_PATH = Path("models/time_torch_weights.pt")

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predict time to complete a GPX route based on historical activities.",
    )
    parser.add_argument("datadir", type=Path, help="Directory containing activity parquet files")
    parser.add_argument("gpxfile", type=Path, help="GPX file to predict time for")
    return parser.parse_args(argv)


def iter_activity_dfs(activity_dir: Path) -> Iterable[tuple[Path, pd.DataFrame]]:
    for parquet_path in sorted(activity_dir.glob("*.parquet")):
        try:
            df = pd.read_parquet(parquet_path)
        except Exception as e:
            sys.stderr.write(f"[warn] Skipping {parquet_path}: {e}\n")
            continue
        yield parquet_path, df


def model_speed_mph(df: pd.DataFrame, model: PaceModel) -> float:
    if not {DISTANCE_M_COL, ELAPSED_TIME_S_COL} <= set(df.columns):
        return float("nan")
    speed_mps = model.func(df[DISTANCE_M_COL], df[ELAPSED_TIME_S_COL])
    if pd.isna(speed_mps):
        return float("nan")
    return float(speed_mps * MPS_TO_MPH_MULTIPLIER)


def evaluate_pace_models(activity_dir: Path) -> dict[str, float]:
    activities = list(iter_activity_dfs(activity_dir))
    if not activities:
        sys.stderr.write(f"No parquet activities found in {activity_dir}.\n")
        return {}

    results: dict[str, float] = {}
    for model in PACE_MODELS:
        speeds = [model_speed_mph(df, model) for _, df in activities]
        speeds = [s for s in speeds if pd.notna(s) and s > 0]
        if not speeds:
            sys.stderr.write(f"[warn] Model {model.name} had no usable activities.\n")
            continue
        results[model.name] = float(np.mean(speeds))
    return results


def load_linear_model(weights_path: Path) -> time_linear.LinearTimeModel | None:
    if not weights_path.exists():
        sys.stderr.write(
            f"[warn] Linear model weights not found at {weights_path}. Run the training notebook to generate them.\n"
        )
        return None

    try:
        return time_linear.load_model(weights_path)
    except Exception as exc:  # pragma: no cover - defensive load guard
        sys.stderr.write(f"[warn] Failed to load linear model weights: {exc}\n")
        return None


def load_torch_model(
    weights_path: Path,
    device: str | None = None,
) -> tuple[time_torch.TimeMLP, dict[str, np.ndarray]] | None:
    if not weights_path.exists():
        sys.stderr.write(
            f"[warn] Torch model weights not found at {weights_path}. Run the training notebook to generate them.\n"
        )
        return None

    try:
        return time_torch.load_model(weights_path, device=device)
    except Exception as exc:  # pragma: no cover - defensive load guard
        sys.stderr.write(f"[warn] Failed to load torch model weights: {exc}\n")
        return None


def print_predictions(
    distance_mi: float,
    model_speeds: dict[str, float],
    linear_model: time_linear.LinearTimeModel | None,
    torch_model_bundle: tuple[time_torch.TimeMLP, dict[str, np.ndarray]] | None,
    gpx_elev_gain_ft: float,
) -> None:
    if not model_speeds and linear_model is None and torch_model_bundle is None:
        sys.stderr.write("No model produced a prediction.\n")
        return

    if model_speeds:
        for name, speed_mph in model_speeds.items():
            pace_min_per_mile = 60.0 / speed_mph if speed_mph > 0 else float("nan")
            eta_hours = distance_mi / speed_mph if speed_mph > 0 else float("inf")
            print(
                f"\n[{name}]\n"
                f"  Baseline speed : {speed_mph:.2f} mph\n"
                f"  Baseline pace  : {pace_min_per_mile:.2f} min/mi\n"
                f"  Predicted time : {hours_to_hhmmss(eta_hours)}"
            )

    if linear_model is not None:
        feature_values = dict(zip(linear_model.feature_names, linear_model.feature_means))
        feature_values["distance_mi"] = distance_mi
        feature_values["elevation_gain_ft"] = gpx_elev_gain_ft

        eta_hours = linear_model.predict_hours(feature_values)

        if eta_hours <= 0 or np.isnan(eta_hours) or np.isinf(eta_hours):
            print("\n[linear_time_model]\n  Prediction invalid (non-positive time).")
        else:
            print(
                "\n[linear_time_model]\n"
                f"  Features       : " + ", ".join(f"{k}={v:.2f}" for k, v in feature_values.items()) + "\n"
                f"  Coefficients   : " + ", ".join(f"{k}={v:.4f}" for k, v in zip(linear_model.feature_names, linear_model.coefficients)) + "\n"
                f"  Predicted time : {hours_to_hhmmss(eta_hours)}"
            )

    if torch_model_bundle is not None:
        torch_model, stats = torch_model_bundle
        feature_names = stats["feature_names"].tolist()
        base_values = dict(zip(feature_names, stats["mean"].tolist()))
        if "distance_mi" in base_values:
            base_values["distance_mi"] = distance_mi
        if "elevation_gain_ft" in base_values:
            base_values["elevation_gain_ft"] = gpx_elev_gain_ft

        eta_hours = time_torch.predict_hours(torch_model, stats, base_values)
        if eta_hours <= 0 or np.isnan(eta_hours) or np.isinf(eta_hours):
            print("\n[torch_time_model]\n  Prediction invalid (non-positive time).")
        else:
            print(
                "\n[torch_time_model]\n"
                f"  Predicted time : {hours_to_hhmmss(eta_hours)}"
            )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.datadir.exists() or not args.datadir.is_dir():
        sys.stderr.write(f"Directory {args.datadir} does not exist or is not a directory.\n")
        return 2
    if not args.gpxfile.exists() or not args.gpxfile.is_file():
        sys.stderr.write(f"GPX file {args.gpxfile} does not exist or is not a file.\n")
        return 2

    try:
        distance_mi, elev_gain_ft = gpxu.route_summary(args.gpxfile, metric=False)
    except Exception as e:
        sys.stderr.write(f"Failed to read GPX file: {e}\n")
        return 1

    print(f"Loaded GPX file: '{args.gpxfile}' ({distance_mi:.2f} mi, {elev_gain_ft:.0f} ft gain)")

    model_speeds = evaluate_pace_models(args.datadir)
    linear_model = load_linear_model(DEFAULT_LINEAR_MODEL_PATH)
    torch_model_bundle = load_torch_model(DEFAULT_TORCH_MODEL_PATH)
    print_predictions(distance_mi, model_speeds, linear_model, torch_model_bundle, elev_gain_ft)

    return 0 if model_speeds or linear_model or torch_model_bundle else 1


if __name__ == "__main__":
    sys.exit(main())
