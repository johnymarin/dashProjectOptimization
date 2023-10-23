import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp

# https://www.youtube.com/watch?v=kWRGkC0I3B4&t=319s


from dash.dependencies import Input, Output, State
from dash.dash_table.Format import Format, Scheme, Sign, Symbol


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

comparison_options = ['<', '<=', '>', '>=', '=', '!=']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

initial_data = [
    {'operation': 'Objective Function', 'x1': 10, 'x2': 20, },
    {'operation': 'Constraint 1', 'x1': 4, 'x2': 2, 'EQ': '<=', 'limit': 20 },
    {'operation': 'Constraint 2', 'x1': 8, 'x2': 8, 'EQ': '<=', 'limit': 20 },
    {'operation': 'Constraint 3',  'x2': 2, 'EQ': '<=', 'limit': 10 },
]


app.layout = html.Div([
    html.H1('Linear Programming Solver'),
    dcc.Store(id='variable-counter', data=2),
    dcc.Store(id='constraint-counter', data=3),
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
            data= initial_data,
            editable=True,
            row_deletable=True
        ),
        html.Button('Add Variable', id='add-variable-button', n_clicks=0),
        html.Button('Add Constraint', id='add-constraint-button', n_clicks=0),
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='output-standard-form',
                 children='Enter the values and press submit')
    ])
])



@app.callback(
    [Output('objective-function-table', 'columns'),
     Output('objective-function-table', 'data'),
     Output('output-standard-form', 'children')],
    [Input('add-variable-button', 'n_clicks'),
     Input('add-constraint-button', 'n_clicks'),
     Input('submit-val', 'n_clicks')],
    [State('objective-function-table', 'columns'),
     State('objective-function-table', 'data'),
     State('variable-counter', 'data'),
     State('constraint-counter', 'data')]
)
def update_table(add_variable_clicks, add_constraint_clicks, submit_clicks, columns, data, variable_counter, constraint_counter):
    ctx = dash.callback_context
    if ctx.triggered_id:
        if 'add-variable-button' in ctx.triggered_id:
            if add_variable_clicks is not None:
                variable_counter += add_variable_clicks
                new_variable_id = f'x{variable_counter}'
                columns.insert(-2, {'id': new_variable_id, 'name': new_variable_id, 'editable': True})
        elif 'add-constraint-button' in ctx.triggered_id:
            if add_constraint_clicks is not None:
                constraint_counter += add_constraint_clicks
                new_row = {'operation': f'Constraint {constraint_counter}', 'x1': '', 'x2': '', 'EQ': '', 'limit': ''}
                data.append(new_row)
        elif 'submit-val' in ctx.triggered_id:
            if submit_clicks is not None:
                obj_func = 'z = 10*x1 +20*x2'
                dec_vars = ['x1', 'x2']
                max_min = 'max'
                constraints = [
                    '+4*x1 +2*x2 <= 20',
                    '+8*x1 +8*x2 <= 20',
                    '+2*x2 <= 10'
                ]
                obj_func = 'z = 10*x1 +20*x2'

                output_text = f'''
                Objetive Funcion: {obj_func}
                desition variables: x1, x2 
                Maximize z
                Constraints: 
                    '+4*x1 +2*x2 <= 20'
                    '+8*x1 +8*x2 <= 20'
                    '+2*x2 <= 10'
                Slack variables: s1, s2, s3
                '''
                return columns, data, output_text

    return columns, data, dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)


