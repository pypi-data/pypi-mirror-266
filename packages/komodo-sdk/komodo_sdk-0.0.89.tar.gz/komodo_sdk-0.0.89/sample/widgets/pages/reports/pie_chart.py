import dash

dash.register_page(__name__)

import pandas as pd
import plotly.express as px
from dash import dcc, html

# Sample financial data for a portfolio
df = pd.DataFrame({
    "Investment Type": ["Stocks", "Bonds", "Real Estate", "Commodities", "Cryptocurrency"],
    "Value": [50000, 20000, 30000, 10000, 15000]
})

# Generate the pie chart
fig = px.pie(df, names="Investment Type", values="Value", title="Portfolio Distribution")


def layout(**kwargs):
    return html.Div([
        dcc.Graph(
            id='portfolio-distribution-pie',
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
