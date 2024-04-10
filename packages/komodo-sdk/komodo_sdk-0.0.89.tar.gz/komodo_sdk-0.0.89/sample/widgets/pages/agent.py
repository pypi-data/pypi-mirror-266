import dash

from sample.widgets.globals import get_agents, get_agent_response

dash.register_page(__name__)

from dash import dcc, html, Output, Input, State


# Placeholder for calling a generator function with the selected agent and question
# In practice, replace this with your actual function call


def layout(**kwargs):
    agents = get_agents()

    return html.Div([
        html.H3('Komodo Agents', style={'textAlign': 'center'}),
        html.Div('Select an available agent:', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='agent-dropdown',
            options=[{'label': agent.name, 'value': agent.shortcode} for agent in agents],
            value=agents[0].shortcode if agents else None,
            style={'marginRight': 'auto', 'marginLeft': 'auto', 'width': '50%'}
        ),
        html.Div('Ask a question:', style={'textAlign': 'center', 'marginTop': '20px'}),
        dcc.Textarea(
            id='question-input',
            style={'width': '60%', 'height': '100px', 'marginRight': 'auto', 'marginLeft': 'auto', 'padding': '10px'},
            placeholder='Type your question here...'
        ),
        html.Button('Submit', id='submit-button',
                    style={'display': 'block', 'marginRight': 'auto', 'marginLeft': 'auto', 'marginTop': '10px'}),
        html.Div(id='response-output', style={
            'whiteSpace': 'pre-line',
            'border': '1px solid #CCC',
            'padding': '10px',
            'marginTop': '20px',
            'marginRight': 'auto',
            'marginLeft': 'auto',
            'width': '60%',
            'minHeight': '100px',
            'textAlign': 'left',
            'backgroundColor': '#F9F9F9'
        })
    ], style={
        'maxWidth': '800px',
        'margin': '0 auto',
        'padding': '20px',
        'textAlign': 'center'
    })

    # Assuming `app` is your Dash app instance


@dash.callback(
    Output('response-output', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('agent-dropdown', 'value'), State('question-input', 'value')],
    prevent_initial_call=True
)
def update_response(n_clicks, selected_agent, question):
    response = get_agent_response(selected_agent, question)
    return response
