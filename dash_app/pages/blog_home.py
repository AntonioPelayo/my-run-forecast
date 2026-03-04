"""Home page for the my-run-forecast blog."""

from __future__ import annotations

import dash
from dash import html

dash.register_page(__name__, path="/blog_home", name="Running Blog")

layout = html.Div([
    html.H1("Posts"),
    html.P([
        '📊 ',
        html.A(
            "Effort Zone Classification with Lactate Threshold",
            href="../blog/effort_zone_classification"
        )
    ]),
    html.P([
        '🕚 ',
        html.A(
            "My Training Schedule and Habits",
            href="../blog/training_schedule_and_habits"
        )
    ]),
])
