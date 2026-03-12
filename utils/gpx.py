from pathlib import Path

import gpxpy
import geopy.distance
import pandas as pd


def gpx_to_df(gpx_path: Path) -> pd.DataFrame:
    with open(gpx_path, 'r') as f:
        gpx = gpxpy.parse(f)

    gpx_pts = []
    for point in gpx.tracks[0].segments[0].points:
        try:
            elevation = point.elevation
        except AttributeError:
            elevation = 0
        gpx_pts.append((point.latitude, point.longitude, elevation))
    df = pd.DataFrame(gpx_pts, columns=['position_lat', 'position_long', 'elevation'])

    # Cumulative metrics
    coords = [(p.position_lat, p.position_long) for p in df.itertuples()]
    df['distance_change'] = [0] + [
        geopy.distance.distance(x1, x2).m
        for x1, x2 in zip(coords[:-1], coords[1:])
    ]
    df['cum_distance'] = df.distance_change.cumsum()
    if df.elevation.isnull().all():
        df['elevation'] = 0.0
    df['elevation_change'] = df.elevation.diff()
    df['cum_elevation_gain'] = df['elevation_change'].clip(lower=0).cumsum()

    return df


def route_summary(gpx_path: Path) -> tuple[float, float]:
    df = gpx_to_df(gpx_path)
    if df.empty:
        raise RuntimeError(f"GPX contained no route points")

    distance = float(df['cum_distance'].iloc[-1])

    cum_elevation_gain = float(df['cum_elevation_gain'].iloc[-1])

    return distance, cum_elevation_gain
