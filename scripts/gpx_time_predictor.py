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
from utils import gpx as gu
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


def print_predictions(distance_mi: float, model_speeds: dict[str, float]) -> None:
    if not model_speeds:
        sys.stderr.write("No model produced a baseline speed.\n")
        return

    for name, speed_mph in model_speeds.items():
        pace_min_per_mile = 60.0 / speed_mph if speed_mph > 0 else float("nan")
        eta_hours = distance_mi / speed_mph if speed_mph > 0 else float("inf")
        print(
            f"\n[{name}]\n"
            f"  Baseline speed : {speed_mph:.2f} mph\n"
            f"  Baseline pace  : {pace_min_per_mile:.2f} min/mi\n"
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
        distance_mi, elev_gain_ft = gu.route_summary(args.gpxfile, metric=False)
    except Exception as e:
        sys.stderr.write(f"Failed to read GPX file: {e}\n")
        return 1

    print(f"Loaded {args.gpxfile} ({distance_mi:.2f} mi, {elev_gain_ft:.0f} ft gain)")

    model_speeds = evaluate_pace_models(args.datadir)
    print_predictions(distance_mi, model_speeds)

    return 0 if model_speeds else 1


if __name__ == "__main__":
    sys.exit(main())
