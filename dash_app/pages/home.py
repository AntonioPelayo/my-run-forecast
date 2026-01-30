"""Home page for the my-run-forecast dashboard."""

from __future__ import annotations

import dash
from dash import dcc, html


dash.register_page(__name__, path="/", name="Home")


layout = html.Div(
    html.P(children=[
        "💻 ",
        html.A(
            "Project GitHub",
            href="https://github.com/AntonioPelayo/my-run-forecast",
            target="_blank"
        )
    ])
)
