from __future__ import annotations

import dash
from dash import Dash, dcc, html

app: Dash = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
)
server = app.server

app.layout = html.Div(
    [
        html.Nav([
            html.A("Home", href="/", style={"marginRight": "1rem"}),
            html.A("Project GitHub", href="https://github.com/AntonioPelayo/my-run-forecast", target="_blank" , style={"marginRight": "1rem"}),
            html.A("Blog", href="/blog_home", style={"marginRight": "1rem"}),
            html.A("GPX Route Completion Time Predictor", href="/gpx_time_predictor", style={"marginRight": "1rem"}),
        ]),
        dash.page_container,
    ],
)


if __name__ == "__main__":
    app.run()
