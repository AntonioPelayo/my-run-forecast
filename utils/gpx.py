from pathlib import Path

import gpxpy
import geopy.distance
import pandas as pd


def gpx_to_df(gpx_path: Path) -> pd.DataFrame:
    with open(gpx_path, 'r') as f:
        gpx = gpxpy.parse(f)

    gpx_pts = []
    for point in gpx.tracks[0].segments[0].points:
        gpx_pts.append((point.latitude, point.longitude, point.elevation))
    df = pd.DataFrame(gpx_pts, columns=['position_lat', 'position_long', 'altitude'])

    # Cumulative metrics
    coords = [(p.position_lat, p.position_long) for p in df.itertuples()]
    df['distance_change'] = [0] + [
        geopy.distance.distance(x1, x2).m
        for x1, x2 in zip(coords[:-1], coords[1:])
    ]
    df['cum_distance'] = df.distance_change.cumsum()
    df['altitude_change'] = df.altitude.diff()
    df['cum_altitude_gain'] = df['altitude_change'].clip(lower=0).cumsum()

    return df


def route_summary(gpx_path: Path) -> tuple[float, float]:
    df = gpx_to_df(gpx_path)
    if df.empty:
        raise RuntimeError(f"GPX contained no route points")

    distance = float(df['cum_distance'].iloc[-1])
    cum_altitude_gain = float(df['cum_altitude_gain'].iloc[-1])

    return distance, cum_altitude_gain
