import dash
from dash import html

dash.register_page(
    __name__,
    path="/archive",
    redirect_from=["/archive-2021", "/archive-2020"]
)


def layout(report_id=None, department_id=None, **other_unknown_query_strings):
    return html.Div([
        html.H1('This is our Archive page'),
        html.Div(f'''
	    This is report: {report_id}.\n
	    This is department: {department_id}.
	    '''),
    ])
