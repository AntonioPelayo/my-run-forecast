from __future__ import annotations

import base64
import io

import dash
from dash import Input, Output, dcc, html
from fitparse import FitFile

from utils.fit import fit_to_df, standardize_fit_df
from utils.plots import plot_run

dash.register_page(__name__, path="/activity_analysis", name="Activity Analysis")


def _empty_figure():
    return {
        "data": [],
        "layout": {
            "title": {"text": "Upload a .fit file to see the activity's route map"},
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


layout = html.Div(
    [
        html.H2("Activity Analysis"),
        dcc.Upload(
            id="fit-upload",
            children=html.Div(
                [
                    "Drag and drop a .fit file here, or ",
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
            accept=".fit",
            multiple=False,
        ),
        html.Div(id="fit-upload-status", style={"marginBottom": "1rem"}),
        dcc.Graph(id="fit-plot", figure=_empty_figure()),
    ]
)


@dash.callback(
    Output("fit-plot", "figure"),
    Output("fit-upload-status", "children"),
    Input("fit-upload", "contents"),
    Input("fit-upload", "filename"),
)
def update_plot(contents, filename):
    if contents is None:
        return _empty_figure(), "Waiting for a .fit upload."

    if not filename or not filename.lower().endswith(".fit"):
        return _empty_figure(), "Please upload a .fit file."

    try:
        _, content_string = contents.split(",", 1)
        data = base64.b64decode(content_string)
        fit = FitFile(io.BytesIO(data))
        df = fit_to_df(fit)
        if not df.empty:
            df = standardize_fit_df(df)

        if df.empty or "position_lat" not in df.columns or "position_long" not in df.columns:
            return _empty_figure(), "No GPS data found in this .fit file."

        fig = plot_run(df, title=f"Activity: {filename}")
        return fig, f"Loaded {filename}."
    except Exception as exc:
        return _empty_figure(), f"Failed to parse {filename}: {exc}"
