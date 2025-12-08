import numpy as np
import pandas as pd

def elapsed_seconds(timestamps: pd.Series) -> pd.Series:
    """Compute seconds elapsed from a series of timestamps."""
    timestamps = pd.to_datetime(timestamps, errors='coerce')
    t0 = timestamps.dropna().min()
    if pd.isna(t0):
        return pd.Series([np.nan] * len(timestamps))
    return (timestamps - t0).dt.total_seconds()


def compute_gradient(altitude_col: pd.Series, distance_col: pd.Series) -> pd.DataFrame:
    """Compute gradients using either metric (meters) or imperial (feet/miles) inputs."""
    da = altitude_col.diff().fillna(0)
    dd = distance_col.diff().fillna(0).replace(0, 1e-6)
    return da / dd


def percent_grade(gradient: pd.Series) -> pd.Series:
    return gradient * 100


def grade_degrees(gradient: pd.Series) -> pd.Series:
    return np.degrees(np.arctan(gradient))


def semicircle_to_degrees(s: pd.Series) -> pd.Series:
    """Convert a series of semicircles to degrees for lat/long."""
    return s * (180.0 / 2**31)
