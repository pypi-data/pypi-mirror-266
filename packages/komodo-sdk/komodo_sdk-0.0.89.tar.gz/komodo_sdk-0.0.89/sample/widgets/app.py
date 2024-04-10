import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, Output, Input, dcc

from sample.widgets.globals import load_user_preferences, save_user_preferences
from sample.widgets.themes import Themes

prefs = load_user_preferences()
theme = Themes.from_string(prefs.get('theme', 'JOURNAL')).value
print(f"Selected theme: {theme}")

app = Dash(__name__, use_pages=True,
           url_base_pathname="/widgets/",
           suppress_callback_exceptions=True,
           external_stylesheets=[theme])

server = app.server

navbar = dbc.NavbarSimple([
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(theme.name, id=f"theme-{theme.name}") for theme in Themes
        ],
        nav=True,
        in_navbar=True,
        label="Select Theme",
    ),
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page['name'], href=page['relative_path'])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="More Pages",
    )],
    brand="Komodo AI Platform SDK",
    color="primary",
    dark=True,
    className="mb-0",
    fluid=True,
)

app.layout = html.Div([
    navbar,
    html.Div(dash.page_container, className='container-padding-margin'),
    html.Link(rel='stylesheet', id='theme-link', href=dbc.themes.BOOTSTRAP)
])


# Callback to update the theme based on selection
@app.callback(
    Output('theme-link', 'href'),
    [Input(f"theme-{theme.name}", "n_clicks") for theme in Themes],
    prevent_initial_call=True,
)
def update_theme(*args):
    ctx = dash.callback_context
    theme_name = Themes.BOOTSTRAP.name
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        theme_name = button_id.replace('theme-', '')

    prefs = load_user_preferences()
    prefs['theme'] = theme_name
    save_user_preferences(prefs)
    dcc.Location = dcc.Location
    return Themes.from_string(theme_name).value
