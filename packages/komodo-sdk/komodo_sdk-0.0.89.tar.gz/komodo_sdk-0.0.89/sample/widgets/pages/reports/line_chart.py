import dash

dash.register_page(__name__)

import pandas as pd
import numpy as np
import plotly.express as px
from dash import dcc, html

# Simulate stock price data for three companies over two years
dates = pd.date_range(start="2022-01-01", end="2023-12-31", freq='W')
data = {
    "Date": dates,
    "Company A": (pd.Series(range(len(dates))) * 1.2 + (
            pd.Series(range(len(dates))) * pd.Series(range(len(dates))).apply(
        lambda x: np.sin(x / 52.0)) * 5)).tolist(),
    "Company B": (pd.Series(range(len(dates))) * 1.1 + (
            pd.Series(range(len(dates))) * pd.Series(range(len(dates))).apply(
        lambda x: np.sin((x + 10) / 50.0)) * 4)).tolist(),
    "Company C": (pd.Series(range(len(dates))) * 1.3 + (
            pd.Series(range(len(dates))) * pd.Series(range(len(dates))).apply(
        lambda x: np.cos(x / 45.0)) * 3)).tolist(),
}

df = pd.DataFrame(data)
df_melted = df.melt(id_vars="Date", var_name="Company", value_name="Stock Price")

# Generate the line chart
fig = px.line(df_melted, x="Date", y="Stock Price", color="Company", title="Stock Prices Over Time")


def layout(report_id=None, **kwargs):
    return html.Div([
        dcc.Graph(
            id='stock-prices-line-chart',
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

# Note: Integration of this layout function into a Dash app requires defining an app instance
