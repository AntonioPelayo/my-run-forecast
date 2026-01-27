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
        html.H1("My Run Forecast"),
        html.Nav(_nav_links(), style={"marginBottom": "1.5rem"}),
        dash.page_container,
    ],
    style={"maxWidth": "960px", "margin": "0 auto", "padding": "2rem 1rem"},
)


if __name__ == "__main__":
    app.run()
