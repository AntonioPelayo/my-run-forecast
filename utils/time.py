"""Time formatting utilities."""

import numpy as np

from utils.config import M_TO_KM_MULTIPLIER, M_TO_MI_MULTIPLIER

def hours_to_hhmmss(hours: float) -> str:
    """Convert decimal hours to an hh:mm:ss string."""
    total_seconds = int(hours * 3600)
    hours_component = total_seconds // 3600
    minutes_component = (total_seconds % 3600) // 60
    seconds_component = total_seconds % 60
    return f"{hours_component:d}:{minutes_component:02d}:{seconds_component:02d}"


def seconds_to_hours(seconds: float) -> float:
    """Convert seconds to decimal hours."""
    return seconds / 3600.0 if not np.isnan(seconds) else float('nan')


def format_seconds_to_pace(distance_m: float, elapsed_seconds: float, metric=True) -> str:
    """Format pace as min/km or min/mi."""
    if np.isnan(elapsed_seconds) or distance_m <= 0:
        return "N/A"
    if metric:
        pace_seconds_per_km = elapsed_seconds / (distance_m * M_TO_KM_MULTIPLIER)
        pace_minutes = int(pace_seconds_per_km // 60)
        pace_seconds = int(pace_seconds_per_km % 60)
        return f"{pace_minutes}:{pace_seconds:02d} min/km"
    else:
        distance_mi = distance_m * M_TO_MI_MULTIPLIER
        pace_seconds_per_mi = elapsed_seconds / distance_mi
        pace_minutes = int(pace_seconds_per_mi // 60)
        pace_seconds = int(pace_seconds_per_mi % 60)
        return f"{pace_minutes}:{pace_seconds:02d} min/mi"
