"""Home page for the my-run-forecast blog."""

from __future__ import annotations

import dash
from dash import html

dash.register_page(__name__, path="/blog_home", name="Running Blog")

layout = html.Div([
    html.P([
        html.H1("Posts"),
        html.A(
            "Effort Zone Classification with Lactate Threshold",
            href="../blog/effort_zone_classification"
        )
    ]),
])
