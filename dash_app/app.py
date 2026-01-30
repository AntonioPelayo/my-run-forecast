"""
Dash entry point for the run-forecast dashboard.

Run with:
    python -m dash_app.app
"""

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

def _nav_links() -> list[html.A]:
    """Build a simple nav bar from the registered pages."""
    links: list[html.A] = []
    for page in dash.page_registry.values():
        links.append(
            html.A(
                page["name"],
                href=page["path"],
                style={"marginRight": "1rem"},
            )
        )
    return links


app.layout = html.Div(
    [
        html.Nav(_nav_links()),
        html.H1("My Run Forecast"),
        dash.page_container,
    ],
)


if __name__ == "__main__":
    app.run()
    # app.run(debug=True)
