"""Home page for the my-run-forecast dashboard."""

from __future__ import annotations

import dash
from dash import html


dash.register_page(__name__, path="/", name="Home")


layout = html.Div([
    html.H1("My Run Forecast"),
    html.H2("Analysis and tools for my personal running data"),
    html.P("Click a link in the navigation bar")
])
