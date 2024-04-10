import json  # Handle JSON operations

import dash
from dash import dcc, html, Output, Input, State, callback

from komodo.shared.documents.text_extract import extract_json
from sample.widgets.globals import get_agent_response, get_json_markup

dash.register_page(__name__)

model_output_layout = {
    "type": "div",
    "children": [
        {
            "type": "graph",
            "id": "pie-chart-1",
            "figure": {
                "data": [
                    {
                        "values": [19, 26, 55],
                        "labels": ["Category A", "Category B", "Category C"],
                        "type": "pie",
                        "hoverinfo": "label+percent+name",
                        "textinfo": "none"
                    }
                ],
                "layout": {
                    "title": "Pie Chart 1"
                }
            }
        },
        {
            "type": "graph",
            "id": "pie-chart-2",
            "figure": {
                "data": [
                    {
                        "values": [45, 25, 30],
                        "labels": ["Region X", "Region Y", "Region Z"],
                        "type": "pie",
                        "hoverinfo": "label+percent+name",
                        "textinfo": "none"
                    }
                ],
                "layout": {
                    "title": "Pie Chart 2"
                }
            }
        },
        {
            "type": "graph",
            "id": "pie-chart-3",
            "figure": {
                "data": [
                    {
                        "values": [10, 20, 70],
                        "labels": ["Product 1", "Product 2", "Product 3"],
                        "type": "pie",
                        "hoverinfo": "label+percent+name",
                        "textinfo": "none"
                    }
                ],
                "layout": {
                    "title": "Pie Chart 3"
                }
            }
        }
    ]
}

from dash import dash_table


def create_component(component_def):
    if component_def['type'] == 'div':
        children = [create_component(child) for child in component_def.get('children', [])]
        return html.Div(children=children)
    elif component_def['type'] == 'graph':
        return dcc.Graph(id=component_def['id'], figure=component_def['figure'])
    elif component_def['type'] == 'table':
        return dash_table.DataTable(id=component_def['id'], columns=component_def['columns'],
                                    data=component_def['data'])
    elif component_def['type'] == 'row':
        children = [create_component(child) for child in component_def.get('children', [])]
        return html.Div(children=children, style={'display': 'flex', 'flexDirection': 'row'})
    elif component_def['type'] == 'column':
        children = [create_component(child) for child in component_def.get('children', [])]
        return html.Div(children=children, style={'display': 'flex', 'flexDirection': 'column'})


def layout(**kwargs):
    return html.Div([
        html.Div([
            html.Div('Talk to Dasher v1.0', style={'textAlign': 'center', 'marginTop': '20px'}),
            dcc.Textarea(
                id='prompt-input',
                style={'width': '100%', 'height': '100px', 'marginRight': 'auto', 'marginLeft': 'auto',
                       'padding': '10px'},
                placeholder='Type your instruction here...'
            ),
            html.Button('Submit', id='submit-button-dasher',
                        style={'display': 'block', 'marginRight': 'auto', 'marginLeft': 'auto', 'marginTop': '10px'}),
        ], style={'width': '70%', 'marginRight': 'auto', 'marginLeft': 'auto', 'marginTop': '20px',
                  'backgroundColor': '#f6f8fa', 'padding': '20px', 'borderRadius': '10px',
                  'border': '1px solid black', 'boxShadow': '5px 5px 5px gray'}),
        html.Hr(),
        html.Div(
            id='response-output-dasher',
            style={
                'width': '70%',  # Ensures the div takes up 100% of the screen width
                'overflow-x': 'hidden',  # Prevents horizontal scrolling
                'overflow-y': 'auto',  # Enables vertical scrolling if content overflows
                'marginRight': 'auto',
                'marginLeft': 'auto',
                'paddingBottom': '100px',
                'marginBottom': '200px',
            },
            children=[
                html.Div([
                    create_component(model_output_layout)
                ],
                    style={'width': '100%'}  # Ensures that children also attempt to fit the width of the parent
                )
            ]
        )])


@callback(
    Output('response-output-dasher', 'children'),
    [Input('submit-button-dasher', 'n_clicks')],
    [State('prompt-input', 'value')],
    prevent_initial_call=True,
    running=[
        (Output('response-output-dasher', 'children'), '', dcc.Loading(type="circle")),  # Clear output and show loading
    ]
)
def update_dashboard(n_clicks, prompt):
    print("Fetching data...")
    agent_shortcode = 'dasher_v1'
    response = get_agent_response(agent_shortcode, prompt)
    response_as_json = json.loads(extract_json(response))

    if 'error' in response_as_json:
        return get_json_markup(response_as_json)

    print("Updating dashboard...")
    try:
        return create_component(response_as_json)
    except Exception as e:
        return get_json_markup({"Could not update the dashboard: ": str(e), "response": response_as_json})
