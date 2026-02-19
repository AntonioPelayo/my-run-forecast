from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from utils.config import (
    M_TO_KM_MULTIPLIER
)
from utils.time import seconds_to_hours, hours_to_hhmmss
from utils.config import PARQUET_RUN_ACTIVITIES_PATH


def get_recent_activities(
    activity_dir: Path=PARQUET_RUN_ACTIVITIES_PATH,
    alphabetical_sort: bool=False,
    limit: int=5
) -> Path | None:
    """Return the most recent parquet activity files in a directory."""
    parquet_files = list(activity_dir.glob('*.parquet'))
    if not parquet_files:
        return None

    if alphabetical_sort:
        parquet_files.sort()
        return parquet_files[-limit:]
    else:
        sorted_files = sorted(parquet_files, key=lambda p: p.stat().st_mtime, reverse=True)
        return sorted_files[:limit]


def activity_summary(activity_file: Path) -> dict[str, float]:
    """Load a single activity parquet file and compute basic summary metrics."""
    try:
        df = pd.read_parquet(activity_file)
    except Exception as exc:  # pragma: no cover - defensive I/O guard
        sys.stderr.write(f"[warn] Skipping {activity_file}: {exc}\n")
        return {}

    if df.empty:
        sys.stderr.write(f"[warn] Activity {activity_file} is empty\n")
        return {}

    elapsed_hours = seconds_to_hours(_final_value(df, 'elapsed_seconds'))
    hhmmss = hours_to_hhmmss(elapsed_hours)

    distance_m = _final_value(df, 'distance')
    if np.isnan(distance_m):
        distance_m = _final_value(df, 'distance_m')

    altitude_col = None
    for name in ('altitude', 'enhanced_altitude', 'altitude_m'):
        if name in df.columns:
            altitude_col = name
            break

    elevation_gain_m = float('nan')
    if altitude_col is not None:
        altitude = df[altitude_col].dropna().astype(float)
        if not altitude.empty:
            elevation_gain_m = float(altitude.diff().clip(lower=0).sum())

    minute_per_km = float('nan')
    if not np.isnan(distance_m) and distance_m > 0 and elapsed_hours > 0:
        total_minutes = elapsed_hours * 60
        total_km = distance_m * M_TO_KM_MULTIPLIER
        minute_per_km = total_minutes / total_km

    activity_date = df['timestamp'].min() if 'timestamp' in df.columns else None

    return {
        'activity_path': str(activity_file),
        'activity_date': activity_date, # GMT start timestamp
        'sport': df['sport'].iloc[0] if 'sport' in df.columns else 'unknown',
        'sub_sport': df['sub_sport'].iloc[0] if 'sub_sport' in df.columns else 'unknown',
        'elapsed_seconds': _final_value(df, 'elapsed_seconds'),
        'elapsed_time': hhmmss,
        'distance': distance_m,
        'trail_distance': distance_m if df['sub_sport'].iloc[0] == 'trail' else 0,
        'cum_altitude_gain': elevation_gain_m,
        'trail_cum_altitude_gain': elevation_gain_m if df['sub_sport'].iloc[0] == 'trail' else 0,
        'average_pace': minute_per_km,
        'average_hr': _mean_value(df, 'heart_rate'),
        'avg_cadence': _mean_value(df, 'cadence'),
        'avg_power': _mean_value(df, 'power'),
    }


def activities_summary(activity_dir: Path) -> pd.DataFrame:
    """Create summaries for every parquet file in a directory."""
    records = []
    for path in sorted(activity_dir.glob('*.parquet')):
        summary = activity_summary(path)
        if not summary:
            continue
        records.append(summary)
    return pd.DataFrame.from_records(records)


def print_activity_summary(activity_file: Path) -> None:
    """Print a summary for a single activity using the loader above."""
    summary = activity_summary(activity_file)
    if not summary:
        return

    elapsed_time = summary.get('elapsed_time', float('nan'))
    distance_m = summary.get('distance_m', float('nan'))
    elevation_m = summary.get('elevation_gain_m', float('nan'))
    distance_value = distance_m * M_TO_KM_MULTIPLIER if not np.isnan(distance_m) else float('nan')
    distance_unit = 'kilometers'
    elevation_value = elevation_m if not np.isnan(elevation_m) else float('nan')
    elevation_unit = 'meters'

    print(f"Activity summary for {activity_file}:")
    if elapsed_time:
        print(f"  Elapsed time: {elapsed_time}")
    if not np.isnan(distance_value):
        print(f"  Distance: {distance_value:.2f} {distance_unit}")
    if not np.isnan(elevation_value):
        print(f"  Elevation gain: {elevation_value:.0f} {elevation_unit}")

    label_suffix = {
        'average_pace': ("Average pace", "min/km"),
        'average_hr': ("Average heart rate", "bpm"),
        'avg_cadence': ("Average cadence", "spm"),
        'avg_power': ("Average power", "watts"),
    }
    for column, (label, suffix) in label_suffix.items():
        value = summary.get(column, float('nan'))
        if np.isnan(value):
            continue
        print(f"  {label}: {value:.1f} {suffix}")


def _final_value(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return float('nan')
    series = df[column]
    if series.empty:
        return float('nan')
    filtered = series.dropna()
    if filtered.empty:
        return float('nan')
    return float(filtered.iloc[-1])


def _mean_value(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return float('nan')
    value = df[column].mean(skipna=True)
    return float(value) if not np.isnan(value) else float('nan')
