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
        html.P("Using my historical running data, you can upload a GPX file of a route and get a predicted time to run it."),
    # Dropdown for 3 pre-uploaded GPX files for testing
        dcc.Dropdown(
            id="gpx-sample-dropdown",
            options=[
                {"label": "BRRC Qualifier Loop", "value": "data/gpx_routes/brrc_qualifier_loop.gpx"},
                {"label": "Gate to tower segment", "value": "data/gpx_routes/gate_to_tower.gpx"},
                {"label": "Pena Passage 10km Route", "value": "data/gpx_routes/pena_passage_10km.gpx"},

            ],
            placeholder="Select a sample GPX route",
            style={"marginBottom": "1rem", "width": "50%"},
        ),
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
        dcc.Checklist(
            id="gpx-trail-toggle",
            options=[{"label": "Trail route", "value": "trail"}],
            style={"marginBottom": "1rem"}
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

    df['idx'] = df.index
    fig = plot_run(df, title="Uploaded GPX Route", color_col="idx")
    return fig


def generate_prediction(gpx_file, is_trail=False):
    distance, cum_altitude_gain = gu.route_summary(gpx_file)
    seconds = predict_elapsed_seconds(
        artifact=load_artifact(Path("gpx_time_prediction_models/artifacts/linear_v1.json")),
        distance=distance,
        cum_altitude_gain=cum_altitude_gain,
        is_trail=is_trail
    )
    hours = tu.seconds_to_hours(seconds)
    hhmmss = tu.hours_to_hhmmss(hours)
    return hhmmss


def _route_summary_text(distance_m: float, gain_m: float) -> str:
    return f"Distance: {distance_m/1000:.2f} km, Altitude Gain: {gain_m:.2f} m"


def _predict_and_plot(gpx_path: str, is_trail=False):
    fig = generate_plot(gpx_path)
    prediction = generate_prediction(gpx_path, is_trail=is_trail)
    distance, cum_altitude_gain = gu.route_summary(gpx_path)
    return fig, prediction, distance, cum_altitude_gain


def _resolve_gpx_source(contents, filename, sample_path):
    if contents and filename and filename.lower().endswith(".gpx"):
        _, content_string = contents.split(",", 1)
        data = base64.b64decode(content_string)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gpx") as tmp:
            tmp.write(data)
            return tmp.name, f"Loaded {filename}."
    if sample_path:
        return sample_path, f"Loaded sample: {Path(sample_path).name}."
    return None, "Waiting for a .gpx upload or sample selection."


@dash.callback(
    Output("gpx-plot", "figure"),
    Output("gpx-upload-status", "children"),
    Output("gpx-route_metrics", "children"),
    Output("gpx-prediction-output", "children"),
    Input("gpx-upload", "contents"),
    Input("gpx-upload", "filename"),
    Input("gpx-sample-dropdown", "value"),
    Input("gpx-trail-toggle", "value"),
)
def update_page(contents, filename, sample_path, is_trail_value):
    gpx_route_metrics = "Distance: N/A, Altitude Gain: N/A"
    prediction_output = "Prediction: N/A"

    gpx_path, status = _resolve_gpx_source(contents, filename, sample_path)
    if gpx_path is None:
        return _empty_figure(), status, gpx_route_metrics, prediction_output

    is_trail = "trail" in (is_trail_value or [])

    try:
        fig, prediction, distance, cum_altitude_gain = _predict_and_plot(gpx_path, is_trail)
        return (
            fig,
            status,
            _route_summary_text(distance, cum_altitude_gain),
            f"Predicted time: {prediction}",
        )
    except Exception as exc:
        return _empty_figure(), f"Failed to parse: {exc}", "", ""
    finally:
        if contents and gpx_path and os.path.exists(gpx_path):
            os.remove(gpx_path)
