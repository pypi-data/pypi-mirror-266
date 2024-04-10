import dash
from dash import html

from sample.widgets.globals import get_appliance, get_version, get_json_markup

dash.register_page(__name__)


def layout():
    appliance = get_appliance()
    agents = appliance.get_all_agents()
    description = {
        "shortcode": appliance.shortcode,
        "name": appliance.name,
        "company": appliance.company,
        "type": appliance.type.name,
        "features": ", ".join([f.name for f in appliance.features]),
        "version": get_version(),
        "purpose": appliance.purpose,
        "agents": [a.summary() for a in agents]
    }

    return html.Div([
        html.H3(appliance.name),
        html.Div(appliance.purpose),
        get_json_markup(description),
    ])
