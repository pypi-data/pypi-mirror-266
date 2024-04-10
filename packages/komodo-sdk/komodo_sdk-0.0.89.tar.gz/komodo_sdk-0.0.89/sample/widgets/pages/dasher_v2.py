import dash

dash.register_page(__name__)

from dash import dash_table
from dash import dcc, html, State, callback
from dash.dependencies import Input, Output
import json

from komodo.shared.documents.text_extract import extract_json
from sample.widgets.globals import get_agent_response, get_json_markup, load_response_list

# Component mapping to their respective Dash component functions
COMPONENT_MAP = {
    'div': html.Div,
    'graph': dcc.Graph,
    'table': dash_table.DataTable,
    'row': lambda children, **kwargs: html.Div(children=children,
                                               style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'},
                                               **kwargs),
    'column': lambda children, **kwargs: html.Div(children=children,
                                                  style={'display': 'flex', 'flexDirection': 'column'}, **kwargs),
    'text': lambda text, **kwargs: html.P(children=text, **kwargs),
    'header': lambda text, level=1, **kwargs: getattr(html, f'H{level}')(children=text, **kwargs),
    'image': html.Img,
    'link': html.A,
    'list': html.Ul,
    'list_item': html.Li,
    'button': html.Button,
    'input': dcc.Input,
    'dropdown': dcc.Dropdown,
    # Add more component mappings here
}


def create_component_v2(component_def, **kwargs):
    """
    Recursively creates Dash components based on a dictionary definition.

    :param component_def: A dict defining the component to create. Must include a 'type'.
    :return: The Dash component.
    """
    if isinstance(component_def, str):
        return component_def

    kwargs = {**component_def, **kwargs}
    if 'type' not in kwargs:
        raise ValueError("Component definition must include a 'type' key.")

    component_type = kwargs['type']
    del kwargs['type']
    if 'props' in kwargs:
        kwargs = kwargs['props']

    if 'style' not in kwargs and component_type in ['graph', 'image']:
        kwargs['style'] = {'flex': 1, 'padding': '10px'}

    if 'text' in kwargs and component_type in ['list_item']:
        kwargs['children'] = kwargs.pop('text')

    if component_type in ['row', 'column', 'div', 'list', 'list_item']:
        children = [create_component_v2(child) for child in kwargs.pop('children', [])]
        return COMPONENT_MAP[component_type](children=children, **kwargs)
    elif component_type in COMPONENT_MAP:
        # Handle components that directly map to Dash components with properties
        if component_type == 'text' or component_type.startswith('header'):
            return COMPONENT_MAP[component_type](**kwargs)
        else:
            return COMPONENT_MAP[component_type](**kwargs)
    else:
        raise ValueError(f"Unsupported component type: {component_type}")


# Example usage:
component_definition = {
    'type': 'div',
    'children': [
        {'type': 'header', 'text': 'Hello World', 'level': 1},
        {'type': 'text', 'text': 'This is a simple text paragraph.'},
        {'type': 'link', 'props': {'href': 'https://www.example.com', 'children': 'Click Here'}},
        {'type': 'image', 'props': {'src': 'https://www.exampleimage.com/image.png', 'alt': 'An example image'}},
        # Add more components as needed
    ]
}


def layout(**kwargs):
    recents = load_response_list('dasher_v2')

    return html.Div([
        html.Div([
            html.Div('Talk to Dasher v2.0',
                     style={'textAlign': 'center', 'marginBottom': '20px'}),

            dcc.Textarea(
                id='prompt-input-v2',
                style={'width': '100%', 'height': '100px', 'marginRight': 'auto', 'marginLeft': 'auto',
                       'padding': '10px'},
                placeholder='Type your instruction here...'
            ),

            html.Div([
                html.Button('Submit', id='submit-button-dasher-v2',
                            style={'marginRight': '10px'}),  # Adjusted marginRight for spacing between items in the row
                html.Div('Select a recent response:', style={'marginRight': '10px', 'alignSelf': 'center'}),
                dcc.Dropdown(
                    id='history-dropdown',
                    options=[{'label': item['prompt'], 'value': item['response']} for item in recents],
                    value=None,
                    style={'flexGrow': 1}  # Allows the dropdown to grow and fill available space
                ),
            ], style={'display': 'flex', 'marginTop': '20px', 'alignItems': 'center'})
            # Flex container with items aligned centrally

        ], style={'width': '70%', 'marginRight': 'auto', 'marginLeft': 'auto', 'marginTop': '20px',
                  'marginBottom': '20px', 'backgroundColor': '#f6f8fa', 'padding': '20px', 'borderRadius': '10px',
                  'border': '1px solid black', 'boxShadow': '5px 5px 5px gray'}),
        html.Hr(),
        html.Div(
            id='response-output-dasher-v2',
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
                    create_component_v2(component_definition_2)
                ],
                    style={'width': '100%'}  # Ensures that children also attempt to fit the width of the parent
                )
            ]
        )])


@callback(
    Output('response-output-dasher-v2', 'children', allow_duplicate=True),
    [Input('submit-button-dasher-v2', 'n_clicks')],
    [State('prompt-input-v2', 'value')],
    prevent_initial_call=True,
    running=[
        (Output('response-output-dasher-v2', 'children'), 'Fetching...', dcc.Loading(type="circle")),
        # Clear output and show loading
    ]
)
def update_dashboard_v2(n_clicks, prompt):
    print("Fetching data...")
    agent_shortcode = 'dasher_v2'
    response = get_agent_response(agent_shortcode, prompt)
    response_as_json = json.loads(extract_json(response))

    if 'error' in response_as_json:
        return get_json_markup(response_as_json)

    print("Updating dashboard...")
    try:
        return create_component_v2(response_as_json)
    except Exception as e:
        return get_json_markup({"Could not update the dashboard: ": str(e), "response": response_as_json})


# Assume other necessary imports and definitions here

@callback(
    Output('response-output-dasher-v2', 'children'),
    [Input('history-dropdown', 'value')],  # Triggered when a new dropdown value is selected
    prevent_initial_call=True,
    allow_duplicate=True  # Allows multiple identical callbacks to run concurrently
)
def update_history_v2(response):
    if response is None:
        return "Please select a value from the dropdown."  # Or any other default message or component

    try:
        response_as_json = json.loads(response)
        if 'error' in response_as_json:
            return get_json_markup(response_as_json)

        print("Updating dashboard...")
        return create_component_v2(response_as_json)

    except Exception as e:
        # This catches JSON parsing errors and errors from create_component_v2
        return get_json_markup({"error": "Could not update the dashboard", "message": str(e)})


component_definition_2 = {
    "type": "div",
    "children": [
        {
            "type": "header",
            "text": "Stock Market Volatility Report",
            "level": 1
        },
        {
            "type": "graph",
            "id": "volatility-graph",
            "figure": {
                "data": [
                    {
                        "x": ["2023-03-01", "2023-03-02", "2023-03-03", "2023-03-04", "2023-03-05", "2023-03-06",
                              "2023-03-07", "2023-03-08", "2023-03-09", "2023-03-10"],
                        "y": [1.2, 1.5, 2.1, 2.5, 1.8, 2.2, 2.7, 3.0, 2.5, 2.3],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": "S&P 500",
                        "marker": {
                            "color": "blue",
                            "size": 8
                        }
                    },
                    {
                        "x": ["2023-03-01", "2023-03-02", "2023-03-03", "2023-03-04", "2023-03-05", "2023-03-06",
                              "2023-03-07", "2023-03-08", "2023-03-09", "2023-03-10"],
                        "y": [1.0, 1.3, 1.9, 2.3, 2.0, 1.9, 2.5, 2.8, 2.4, 2.2],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": "NASDAQ",
                        "marker": {
                            "color": "red",
                            "size": 8
                        }
                    }
                ],
                "layout": {
                    "title": "Market Volatility - S&P 500 vs. NASDAQ",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Volatility Index"}
                }
            }
        },
        {
            "type": "text",
            "text": "The above graph displays the daily volatility index for two major stock markets, S&P 500 and NASDAQ, over a recent 10-day period."
        },
        {
            "type": "header",
            "text": "Key Insights",
            "level": 2
        },
        {
            "type": "list",
            "children": [
                {
                    "type": "list_item",
                    "children": "An upward trend in market volatility was observed, peaking on 2023-03-08."
                },
                {
                    "type": "list_item",
                    "children": "Post-peak, a slight decrease in volatility suggests stabilization in the markets."
                },
                {
                    "type": "list_item",
                    "children": "S&P 500 showed higher volatility peaks compared to NASDAQ, indicating sector-based discrepancies."
                }
            ]
        }
    ]
}
