import dash
import dash_bootstrap_components as dbc
from dash import html


def sidebar():
    return html.Div(
        dbc.Nav(
            [
                dbc.NavLink(
                    html.Div(page["name"], className="ms-2"),
                    href=page["relative_path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
                if page["path"].startswith("/topic")
            ],
            vertical=True,
            pills=True,
            className="bg-light",
        )
    )
