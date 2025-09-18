import numpy as np
import pandas as pd


def avg_speed_basic(distance: pd.Series, elapsed_s: pd.Series) -> float:
    """Compute basic average speed, ignoring zero or negative deltas."""
    if len(distance) < 2 or len(elapsed_s) < 2:
        return float('nan')

    total_distance = distance.iloc[-1] - distance.iloc[0]
    total_time = elapsed_s.iloc[-1] - elapsed_s.iloc[0]

    if total_time <= 0 or total_distance < 0:
        return float('nan')

    return float(total_distance / total_time)


def avg_speed_weighted(distance: pd.Series, elapsed_s: pd.Series) -> float:
    """Compute time weighted average speed."""
    dd = np.diff(distance, prepend=distance[0])
    dt = np.diff(elapsed_s, prepend=elapsed_s[0])

    mask = (dt > 0) & (dd >= 0)
    speeds = (dd[mask] / dt[mask])

    return float(speeds.mean())
