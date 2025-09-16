import numpy as np
import pandas as pd

def create_elapsed_time(df: pd.DataFrame, time_col: str = 'timestamp') -> pd.DataFrame:
    """Add an 'elapsed_time_s' column to the DataFrame based on the time_col."""
    df = df.sort_values(by=time_col).reset_index(drop=True)
    df['elapsed_time_s'] = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds()
    return df

def create_gradient(df: pd.DataFrame, altitude_col: str = 'altitude_m', distance_col: str = 'distance_m', metric: bool = True) -> pd.DataFrame:
    """Compute gradients using either metric (meters) or imperial (feet/miles) inputs."""
    df = df.sort_values(by=distance_col).reset_index(drop=True)

    da = df[altitude_col].diff().fillna(0)
    dd = df[distance_col].diff().fillna(0).replace(0, 1e-6)

    if metric:
        # inputs in meters
        df['delta_altitude_m'] = da
        df['delta_distance_m'] = dd
        df['altitude_m'] = df[altitude_col]
        df['gradient'] = df['delta_altitude_m'] / df['delta_distance_m']
    else:
        # inputs in imperial: altitude in feet, distance in miles
        df['delta_altitude_ft'] = da
        df['delta_distance_mi'] = dd
        df['altitude_ft'] = df[altitude_col]
        df['gradient'] = df['delta_altitude_ft'] / (df['delta_distance_mi'] * 5280.0)

    df['gradient_percent'] = df['gradient'] * 100
    df['gradient_deg'] = np.degrees(np.arctan(df['gradient']))

    return df


def semicircle_to_degrees(s: pd.Series) -> pd.Series:
    """Convert a series of semicircles to degrees for lat/long."""
    return s * (180.0 / 2**31)
