"""Time formatting utilities."""

import numpy as np


def hours_to_hhmmss(hours: float) -> str:
    """Convert decimal hours to an hh:mm:ss string."""
    total_seconds = int(hours * 3600)
    hours_component = total_seconds // 3600
    minutes_component = (total_seconds % 3600) // 60
    seconds_component = total_seconds % 60
    return f"{hours_component:d}:{minutes_component:02d}:{seconds_component:02d}"


def seconds_to_hours(seconds: float) -> float:
    """Convert seconds to decimal hours."""
    return seconds / 3600.0 if not np.isnan(seconds) else float("nan")
