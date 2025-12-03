from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import (
    M_TO_FT_MULTIPLIER, M_TO_MI_MULTIPLIER, M_TO_KM_MULTIPLIER
)

def load_activity_summary(activity_file: Path) -> dict[str, float]:
    """Load a single activity parquet file and compute basic summary metrics."""
    try:
        df = pd.read_parquet(activity_file)
    except Exception as exc:  # pragma: no cover - defensive I/O guard
        sys.stderr.write(f"[warn] Skipping {activity_file}: {exc}\n")
        return {}

    if df.empty:
        sys.stderr.write(f"[warn] Activity {activity_file} is empty\n")
        return {}

    elapsed_hours = _to_hours(_final_value(df, "elapsed_time_s"))

    distance_m = _final_value(df, "distance")
    if np.isnan(distance_m):
        distance_m = _final_value(df, "distance_m")

    altitude_col = None
    for name in ("altitude", "enhanced_altitude", "altitude_m"):
        if name in df.columns:
            altitude_col = name
            break
    elevation_gain_m = float("nan")
    if altitude_col is not None:
        altitude = df[altitude_col].dropna().astype(float)
        if not altitude.empty:
            elevation_gain_m = float(altitude.diff().clip(lower=0).sum())

    distance_mi = distance_m * M_TO_MI_MULTIPLIER if not np.isnan(distance_m) else float("nan")
    elevation_gain_ft = elevation_gain_m * M_TO_FT_MULTIPLIER if not np.isnan(elevation_gain_m) else float("nan")
    activity_date = df['timestamp'].min() if 'timestamp' in df.columns else None

    return {
        "activity_path": str(activity_file),
        "activity_date": activity_date, # GMT start timestamp
        "activity_type": df['sport'].iloc[0] if 'sport' in df.columns else "unknown",
        "activity_subtype": df['sub_sport'].iloc[0] if 'sub_sport' in df.columns else "unknown",
        "elapsed_time_hours": elapsed_hours,
        "distance_m": distance_m,
        "distance_mi": distance_mi,
        "elevation_gain_m": elevation_gain_m,
        "elevation_gain_ft": elevation_gain_ft,
        "average_hr": _mean_value(df, "heart_rate"),
        "avg_cadence": _mean_value(df, "cadence"),
        "avg_power": _mean_value(df, "power"),
    }


def load_activity_summaries(activity_dir: Path) -> pd.DataFrame:
    """Load summaries for every parquet file in a directory."""
    records = []
    for path in sorted(activity_dir.glob("*.parquet")):
        summary = load_activity_summary(path)
        if not summary:
            continue
        records.append(summary)
    return pd.DataFrame.from_records(records)


def print_activity_summary(activity_file: Path, metric: bool = False) -> None:
    """Print a summary for a single activity using the loader above."""
    summary = load_activity_summary(activity_file)
    if not summary:
        return

    elapsed_hours = summary.get("elapsed_time_hours", float("nan"))
    distance_m = summary.get("distance_m", float("nan"))
    elevation_m = summary.get("elevation_gain_m", float("nan"))

    if metric:
        distance_value = distance_m * M_TO_KM_MULTIPLIER if not np.isnan(distance_m) else float("nan")
        distance_unit = "kilometers"
        elevation_value = elevation_m if not np.isnan(elevation_m) else float("nan")
        elevation_unit = "meters"
    else:
        distance_value = summary.get("distance_mi", float("nan"))
        distance_unit = "miles"
        elevation_value = summary.get("elevation_gain_ft", float("nan"))
        elevation_unit = "feet"

    print(f"Activity summary for {activity_file}:")
    if not np.isnan(elapsed_hours):
        print(f"  Elapsed time: {elapsed_hours:.2f} hours")
    if not np.isnan(distance_value):
        print(f"  Distance: {distance_value:.2f} {distance_unit}")
    if not np.isnan(elevation_value):
        print(f"  Elevation gain: {elevation_value:.0f} {elevation_unit}")

    label_suffix = {
        "average_hr": ("Average heart rate", "bpm"),
        "avg_cadence": ("Average cadence", "spm"),
        "avg_power": ("Average power", "watts"),
    }
    for column, (label, suffix) in label_suffix.items():
        value = summary.get(column, float("nan"))
        if np.isnan(value):
            continue
        print(f"  {label}: {value:.1f} {suffix}")


def _final_value(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return float("nan")
    series = df[column]
    if series.empty:
        return float("nan")
    filtered = series.dropna()
    if filtered.empty:
        return float("nan")
    return float(filtered.iloc[-1])


def _mean_value(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return float("nan")
    value = df[column].mean(skipna=True)
    return float(value) if not np.isnan(value) else float("nan")


def _to_hours(seconds: float) -> float:
    return seconds / 3600.0 if not np.isnan(seconds) else float("nan")
