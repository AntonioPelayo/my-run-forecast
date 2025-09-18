"""Time formatting utilities."""

from __future__ import annotations


def hours_to_hhmmss(hours: float) -> str:
    """Convert decimal hours to an hh:mm:ss string."""
    total_seconds = int(hours * 3600)
    hours_component = total_seconds // 3600
    minutes_component = (total_seconds % 3600) // 60
    seconds_component = total_seconds % 60
    return f"{hours_component:d}:{minutes_component:02d}:{seconds_component:02d}"
