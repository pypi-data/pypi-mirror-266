import dash
from dash import html

dash.register_page(__name__)


def layout(**kwargs):
    return html.Div([
        html.H1("This is a full-screen Dash Page", style={'textAlign': 'center'}),
        html.P("Your content here", style={'textAlign': 'center'}),
    ], style={
        'width': 'calc(100vw - 30px)',
        'height': 'calc(100vh - 100px)',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'margin': '0 auto'
    })
