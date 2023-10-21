import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp


from dash.dependencies import Input, Output, State
from dash.dash_table.Format import Format, Scheme, Sign, Symbol


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

comparison_options = ['<', '<=', '>', '>=', '=', '!=']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Linear Programming Solver'),
    html.Div([
        html.Label('Maximize or Minimize:'),
        dcc.Dropdown(
            id='max-min-dropdown',
            options=[
                {'label': 'Maximize', 'value': 'max'},
                {'label': 'Minimize', 'value': 'min'}
            ],
            value='max'
        ),
        html.Label('Objective Function:'),
        dash_table.DataTable(
            id='objective-function-table',
            columns=[
                {'id': 'operation', 'name': 'Operation', 'editable': False},
                {'id': 'z', 'name': 'z', 'editable': False},
                {'id': 'x1', 'name': 'x1', 'editable': True},
                {'id': 'x2', 'name': 'x2', 'editable': True},
                {'id': 'EQ', 'name': 'EQ', 'presentation': 'dropdown', 'editable': True, },
                {'id': 'limit', 'name': 'limit', 'editable': True}
            ],

            dropdown= { 'EQ': {'options': [{'label': opt, 'value': opt} for opt in comparison_options]}},
            data=[
                {'operation': 'Objective Function', 'x1': 3, 'x2': 5, },
                {'operation': 'Constraint 1', },
            ],
            editable=True,
            row_deletable=True
        ),
        html.Button('Add Variable', id='add-variable-button', n_clicks=0),
        html.Button('Add Constraint', id='add-constraint-button', n_clicks=0),
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='output-container-button',
                 children='Enter the values and press submit')
    ])
])

variable_counter = 2
constraint_counter = 1

@app.callback(
    Output('objective-function-table', 'columns'),
    [Input('add-variable-button', 'n_clicks')],
    [State('objective-function-table', 'columns')])
def add_variable(n_clicks, columns):
    global variable_counter
    if n_clicks > 0:
        variable_counter += 1
        new_variable_id = f'x{variable_counter}'
        columns.insert(-2, {'id': new_variable_id, 'name': new_variable_id, 'editable': True})
    return columns

@app.callback(
    Output('objective-function-table', 'data'),
    [Input('add-constraint-button', 'n_clicks')],
    [State('objective-function-table', 'data')])
def add_constraint(n_clicks, data):
    global constraint_counter
    if n_clicks > 0:
        constraint_counter += 1
        new_row = {'operation': f'Constraint {constraint_counter}', 'x1': '', 'x2': '', 'EQ': '', 'limit': ''}
        data.append(new_row)
    return data

if __name__ == '__main__':
    app.run_server(debug=True)