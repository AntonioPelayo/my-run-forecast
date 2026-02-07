from __future__ import annotations

from pathlib import Path
import base64
import os
import tempfile

import dash
from dash import Input, Output, dcc, html

from utils.plots import plot_run
from utils import gpx as gu
from utils import time as tu
from gpx_time_prediction_models.inference.predict import (
    load_artifact,
    predict_elapsed_seconds
)

dash.register_page(__name__, path="/gpx_time_predictor", name="GPX Time Predictor")


def _empty_figure():
    return {
        "data": [],
        "layout": {
            "title": {"text": "Upload a .gpx file to see the route"},
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


layout = html.Div(
    [
        html.H2("GPX Time Predictor"),
        dcc.Upload(
            id="gpx-upload",
            children=html.Div(
                [
                    "Drag and drop a .gpx file here, or ",
                    html.A("[click to select]")
                ]
            ),
            style={
                "width": "100%",
                "height": "80px",
                "lineHeight": "80px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "8px",
                "textAlign": "center",
                "marginBottom": "1rem",
            },
            accept=".gpx",
            multiple=False,
        ),
        html.Div(id="gpx-upload-status", style={"marginBottom": "1rem"}),
        dcc.Graph(id="gpx-plot", figure=_empty_figure()),
        html.P(
            id="gpx-route_metrics",
            style={"marginTop": "1rem", "fontWeight": "bold"}
        ),
        html.P(
            id="gpx-prediction-output",
            style={"marginTop": "1rem", "fontWeight": "bold"}
        ),
    ]
)


def generate_plot(gpx_file):
    df = gu.gpx_to_df(gpx_file)

    if df.empty or "position_lat" not in df.columns or "position_long" not in df.columns:
        return _empty_figure()

    fig = plot_run(df, title="Uploaded GPX Route", color_col=None)
    return fig


def generate_prediction(gpx_file):
    distance, cum_altitude_gain = gu.route_summary(gpx_file)
    seconds = predict_elapsed_seconds(
        artifact=load_artifact(Path("gpx_time_prediction_models/artifacts/linear_v1.json")),
        distance=distance,
        cum_altitude_gain=cum_altitude_gain,
        is_trail=False
    )
    hours = tu.seconds_to_hours(seconds)
    hhmmss = tu.hours_to_hhmmss(hours)
    return hhmmss


@dash.callback(
    Output("gpx-plot", "figure"),
    Output("gpx-upload-status", "children"),
    Output("gpx-route_metrics", "children"),
    Output("gpx-prediction-output", "children"),
    Input("gpx-upload", "contents"),
    Input("gpx-upload", "filename"),
)
def update_page(contents, filename):
    gpx_route_metrics = "Distance: N/A, Altitude Gain: N/A"
    prediction_output = "Prediction: N/A"
    if contents is None:
        return _empty_figure(), "Waiting for a .gpx upload.", gpx_route_metrics, prediction_output

    if not filename or not filename.lower().endswith(".gpx"):
        return _empty_figure(), "Please upload a .gpx file.", gpx_route_metrics, prediction_output

    try:
        _, content_string = contents.split(",", 1)
        data = base64.b64decode(content_string)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp:
                tmp.write(data)
                temp_path = tmp.name

                fig = generate_plot(temp_path)
                prediction = generate_prediction(temp_path)
                distance, cum_altitude_gain = gu.route_summary(temp_path)
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        return fig, f"Loaded {filename}.", f"Distance: {distance/1000:.2f} km, Altitude Gain: {cum_altitude_gain:.2f} m", f"Predicted time: {prediction}"
    except Exception as exc:
        return _empty_figure(), f"Failed to parse {filename}: {exc}", "", ""



