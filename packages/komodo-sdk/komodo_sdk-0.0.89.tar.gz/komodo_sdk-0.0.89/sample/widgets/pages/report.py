import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc

dash.register_page(__name__, path_template="/report/<report_id>")

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")


def layout(report_id=None, **kwargs):
    return html.Div([
        dcc.Graph(
            id='sample-graph',
            figure=fig,
            style={'height': '70%', 'width': '70%'}  # Chart fills the container
        ),
    ], style={
        'width': 'calc(100vw - 30px)',
        'height': 'calc(100vh - 100px)',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'margin': '0 auto'
    })
