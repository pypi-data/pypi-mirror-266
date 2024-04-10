import dash

dash.register_page(__name__)
import pandas as pd
import plotly.express as px
from dash import dcc, html

# Sample financial data for the last 3 quarters
data = {
    "Quarter": ["Q1 2023", "Q2 2023", "Q3 2023"],
    "Sales": [12000, 15000, 13000],
    "Profits": [4000, 5000, 4500],
    "Expenses": [8000, 9000, 8500]
}

df = pd.DataFrame(data).melt(id_vars=["Quarter"], var_name="Metric", value_name="Value")

# Generate the bar chart
fig = px.bar(df, x="Quarter", y="Value", color="Metric",
             title="Company's Financial Performance Over the Last 3 Quarters", barmode='group')


def layout(report_id=None, **kwargs):
    return html.Div([
        dcc.Graph(
            id='company-financials-bar-chart',
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

# Assuming you have an existing Dash app instance
# app.layout = layout()  # Use this line if you want to set the entire app layout to this chart
