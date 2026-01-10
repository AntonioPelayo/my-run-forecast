import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def mapbox_center(lat_col: pd.Series, lon_col: pd.Series) -> dict:
    return {
        "lat": (lat_col.min() + lat_col.max()) / 2,
        "lon": (lon_col.min() + lon_col.max()) / 2
    }


def mapbox_zoom(
    lat_col: pd.Series,
    lon_col: pd.Series,
    padding=0.2,
    min_zoom=3,
    max_zoom=16
) -> float:
    lat_min, lat_max = lat_col.min(), lat_col.max()
    lon_min, lon_max = lon_col.min(), lon_col.max()

    lat_span = (lat_max - lat_min) * (1 + padding)
    lon_span = (lon_max - lon_min) * (1 + padding)
    span = max(lat_span, lon_span)

    # zoom heuristic for Web Mercator
    zoom = np.log2(360 / span) - 1
    zoom = float(np.clip(zoom, min_zoom, max_zoom))

    return zoom


def plot_run(
    df,
    lat_col='position_lat',
    lon_col='position_long',
    map_style='satellite',
    color_col='elapsed_seconds',
    color_scale='Viridis',
    title=""
) -> go.Figure:
    fig = px.scatter_map(
        df,
        lat=lat_col,
        lon=lon_col,
        map_style=map_style,
        center=mapbox_center(df[lat_col], df[lon_col]),
        zoom=mapbox_zoom(df[lat_col], df[lon_col]),
        color=color_col,
        color_continuous_scale=color_scale,
        title=title
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    return fig
