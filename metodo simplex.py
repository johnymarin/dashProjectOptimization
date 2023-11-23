import copy
import dash
import pandas as pd
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp
from typing import List, Any

# https://www.youtube.com/watch?v=kWRGkC0I3B4&t=319s
# https://www.youtube.com/watch?v=eLDXXSTM2_c

from dash.dependencies import Input, Output, State
from dash.dash_table.Format import Format, Scheme, Sign, Symbol


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

comparison_options = ['<', '<=', '>', '>=', '=', '!=']

pivot_row_indices = []
pivot_column_id = []

def subtract_row(row1, row2={}, factor=1):
    new_row = {}
    for key in row1:
        if isinstance(row1[key], (int, float)) and isinstance(row2[key],(int, float)):
            new_row[key] = row1[key] - factor * row2.get(key, 0)
            #print(f"mult  {row1[key]} - {factor} * {row2.get(key, 0)}")
        else:
            new_row[key] = row1[key]
            #print(f"fila {row1[key]}")
    return new_row

def find_most_negative_column_index(simplex_data):
    objetive_row = simplex_data[0]
    min_value = float('inf')
    min_index = None
    min_key = None
    for i, (key, value) in enumerate(objetive_row.items()):
        if key.startswith('x') and isinstance(value, (int, float)) and value < min_value:
            min_value = value
            min_index = i
            min_key = key
    #print(f"the minimum value is {min_value} at index {min_index} and is on the key {min_key}")

    return min_index, min_key


def find_min_limit_ratio_row(simplex_data, column):
    min_value = float('inf')
    min_index = None
    min_row_key = None
    for i, row in enumerate(simplex_data[1:]):
        if column in row and row[column] !=0:
            print(f"dividiendo ratio = {row['limit']} / {row[column]}")
            ratio = row['limit'] / row[column]
            if ratio < min_value:
                min_value = ratio
                min_index = i+1
                min_row_key = simplex_data[min_index]['operation']

    #print(f"The minimun value is at indes {min_index} and the operation is {min_row_key}")
    return min_index, min_row_key

def find_pivot_coefficient(simplex_data, column_id, row_id):
    for row in simplex_data:
        if row['operation'] == row_id:
            return row[column_id]
    return None



def is_optimal(simplex_data):
    z_row = simplex_data[0]
    for key, value in z_row.items():
        if key.startswith('x') and isinstance(value, (int, float)) and value < 0:
            return False
    return True

def simplex_iteration(simplex_data, new_pivot_row, pivot_row_id,pivot_column_id):
    updated_simplex_data = []
    for row in simplex_data:

        if (row['operation'] == pivot_row_id):
            updated_row = new_pivot_row
        else:
            updated_row = subtract_row(row, row2=new_pivot_row, factor=row[pivot_column_id])
        updated_simplex_data.append(updated_row)
    return updated_simplex_data

def simplex(maximize: bool, data: List[dict], decision_variables: List[str], slack_variables: List[str]) -> List[Any]:
    initial_simplex_data = copy.deepcopy(data)
    #print(initial_simplex_data)


    all_variables = ['z',  'limit']
    all_variables += decision_variables
    all_variables += slack_variables

    for row in initial_simplex_data:
        for variable in all_variables:
            if variable not in row:
                row[variable]=0


    for key, value in initial_simplex_data[0].items():
        if key == 'z':
            initial_simplex_data[0][key] = 1
        elif isinstance(value, (int, float)):
            initial_simplex_data[0][key] = -1 * value if maximize else value



    for i in range(1, len(slack_variables) + 1):
        initial_simplex_data[i][slack_variables[i-1]] = 1


    for row in initial_simplex_data:
        for key, value in row.items():
            if not value or value == '':
                row[key]=0

    result = [initial_simplex_data]

    iteration_count = 0
    max_iterations = 10

    while not is_optimal(result[-1] ) and iteration_count < max_iterations:
        pivot_column_index, pivot_column_identifier = find_most_negative_column_index(result[-1])
        pivot_row_index, pivot_row_identifier = find_min_limit_ratio_row(result[-1], pivot_column_identifier)
        pivot_coefficient = find_pivot_coefficient(result[-1], pivot_column_identifier, pivot_row_identifier)

        new_pivot_row = copy.deepcopy(result[-1][pivot_row_index])

        for key in new_pivot_row:
            if isinstance(row[key], (int, float)):
                new_pivot_row[key] /= pivot_coefficient

        result.append(simplex_iteration(result[-1], new_pivot_row, pivot_row_identifier, pivot_column_identifier))

        iteration_count += 1

    return result

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

initial_data = [
    {'operation': 'Objective Function', 'z': '', 'x1': 10, 'x2': 20, },
    {'operation': 'Constraint 1', 'x1': 4, 'x2': 2, 'EQ': '<=', 'limit': 20 },
    {'operation': 'Constraint 2', 'x1': 8, 'x2': 8, 'EQ': '<=', 'limit': 20 },
    {'operation': 'Constraint 3',  'x2': 2, 'EQ': '<=', 'limit': 10 },
]

def extract_desition_variables (columns, data):
    dec_vars = set ()
    is_x_in_obj =False
    is_x_in_constr = False
    for row in data:
        if 'EQ' in row and 'limit' in row:
            for col in columns:
                col_id = col['id']


app.layout = html.Div([
    html.H1('Linear Programming Solver'),
    dcc.Store(id='variable-counter', data=2),
    dcc.Store(id='constraint-counter', data=3),
    dcc.Store(id='step-counter', data=0),
    dcc.Store(id='result-array', data=[]),
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
                {'id': 'x1', 'name': 'x1', 'editable': True,  'type': 'numeric', 'selectable': True,},
                {'id': 'x2', 'name': 'x2', 'editable': True, 'type': 'numeric', 'selectable': True,},
                {'id': 'EQ', 'name': 'EQ', 'presentation': 'dropdown', 'editable': True, },
                {'id': 'limit', 'name': 'limit', 'editable': True, 'type': 'numeric'}
            ],

            dropdown= { 'EQ': {'options': [{'label': opt, 'value': opt} for opt in comparison_options]}},
            data= initial_data,
            editable=True,
            row_deletable=True,
            style_data_conditional=(
                [
                    {
                        'if': {'filter_query': '{operation} = "Objective Function"'},
                        'fontWeight': 'bold',
                        'color': 'green',
                    },
                    {
                        'if': {'column_id': 'operation'},
                        'backgroundColor': 'palegreen',
                    },
                ]
                +
                []
            ),
            style_header={
                'backgroundColor': 'darkgreen',
                'color': 'white',
                'fontWeight': 'bold',
            },
            style_header_conditional=(
                [{},{}]
                +
                []
            ),
        ),
        html.Button('Add Variable', id='add-variable-button', n_clicks=0),
        html.Button('Add Constraint', id='add-constraint-button', n_clicks=0),
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='output-standard-form',
                 children='Enter the values and press submit'),
        dash_table.DataTable(
            id='simplex-table',
            column_selectable='single',
            row_selectable='single',
            style_data_conditional=(
                [
                    {
                        'if': {'filter_query': '{operation} = "Objective Function"'},
                        'fontWeight': 'bold',
                        'color': 'green',
                    },
                    {
                        'if': {'column_id': 'operation'},
                        'backgroundColor': 'palegreen',
                    },
                ]
                +
                [{},{},]
            ),
            style_header={
                'backgroundColor': 'darkgreen',
                'color': 'white',
                'fontWeight': 'bold',
            },
            style_header_conditional=(
                [{},{}]
                +
                []
            ),
        ),
        html.Button('Next Step', id='next-step', n_clicks=0),
        html.Button('Prev Step', id='previous-step', n_clicks=0),
    ])
])



@app.callback(
    [Output('objective-function-table', 'columns'),
     Output('objective-function-table', 'data'),
     Output('output-standard-form', 'children'),
     Output('simplex-table', 'columns'),
     Output('simplex-table', 'data'),
     Output('step-counter', 'data'),
     Output('result-array', 'data'),
     Output('simplex-table', 'selected_columns'),
     Output('simplex-table', 'selected_rows'),],
    [Input('add-variable-button', 'n_clicks'),
     Input('add-constraint-button', 'n_clicks'),
     Input('submit-val', 'n_clicks'),
     Input('next-step', 'n_clicks'),
     Input('previous-step', 'n_clicks'),],
    [State('objective-function-table', 'columns'),
     State('objective-function-table', 'data'),
     State('variable-counter', 'data'),
     State('constraint-counter', 'data'),
     State('simplex-table', 'data'),
     State('step-counter', 'data'),
     State('result-array', 'data'),]
)
def update_table(add_variable_clicks, add_constraint_clicks, submit_clicks, next_clicks, prev_clicks,
                 columns, data, variable_counter, constraint_counter, actual_simplex_data, step_counter, result_array):

    ctx = dash.callback_context
    print(ctx.triggered_id, step_counter)
    if ctx.triggered_id:
        if 'add-variable-button' in ctx.triggered_id:
            if add_variable_clicks is not None:
                variable_counter += add_variable_clicks
                new_variable_id = f'x{variable_counter}'
                columns.insert(-2, {'id': new_variable_id, 'name': new_variable_id, 'editable': True, 'type': 'numeric', 'selectable': True,})
        elif 'add-constraint-button' in ctx.triggered_id:
            if add_constraint_clicks is not None:
                constraint_counter += add_constraint_clicks
                new_row = {'operation': f'Constraint {constraint_counter}', 'x1': '', 'x2': '', 'EQ': '', 'limit': ''}
                data.append(new_row)
        elif 'submit-val' in ctx.triggered_id:
            if submit_clicks is not None:
                obj_func = "z = "

                for key, value in data[0].items():
                    if key.startswith('x') and isinstance(value,(int, float)):
                        if value > 0:
                            obj_func += f" + {value}*{key} "
                        elif value < 0:
                            obj_func += f"- {abs(value)}*{key} "

                dec_vars = [f'x{i}' for i in range(1, 1+variable_counter+add_variable_clicks)]
                max_min = 'max'

                constraints = []

                for row in data[1:]:
                    constraint = ''
                    for key, value in row.items():
                        if key.startswith('x') and isinstance(value, (int, float)):
                            if value > 0:
                                constraint += f" + {value}*{key}"
                            if value < 0:
                                constraint += f" - {abs(value)}*{key}"
                        elif key in ('EQ', 'limit'):
                            constraint += f" {value}"
                    constraints.append(constraint)

                slack_variables = [f's{i}' for i in range(1, 1+constraint_counter + add_constraint_clicks  )]

                output_text = f'''
                Objetive Funcion: {obj_func}
                Decision Variables: {', '.join(dec_vars)}
                Maximize or Minimize: {max_min}
                Constraints: 
                    {', '.join(constraints)}
                Slack variables: {', '.join(slack_variables)}
                '''
                simplex_columns = [col for col in columns if col['id'] not in ['operation', 'EQ', 'limit',]]
                simplex_columns += [{'id': s, 'name': s, 'editable':True} for s in slack_variables]
                simplex_columns += [{'id': 'limit', 'name': 'limit', 'editable':True},]
                simplex_data = simplex(True, data, dec_vars, slack_variables)


                na, pivot_column_id = find_most_negative_column_index(simplex_data[step_counter])
                pivot_row_indices, nb = find_min_limit_ratio_row(simplex_data[step_counter], pivot_column_id)

                return columns, data, output_text, simplex_columns, simplex_data[step_counter], step_counter, simplex_data, [pivot_column_id], [pivot_row_indices]

        elif 'next-step' in ctx.triggered_id  and step_counter < len(result_array) - 1:
            na, pivot_column_id = find_most_negative_column_index(result_array[step_counter-1])
            pivot_row_indices, nb = find_min_limit_ratio_row(result_array[step_counter-1], pivot_column_id)
            step_counter += 1

            if step_counter == len(result_array):
                pivot_column_id = []
                pivot_row_indices = []

            return columns, dash.no_update, dash.no_update, dash.no_update, result_array[step_counter], step_counter, dash.no_update, [pivot_column_id], [pivot_row_indices]

        elif 'previous-step' in ctx.triggered_id  and step_counter > 0:
            na, pivot_column_id = find_most_negative_column_index(result_array[step_counter])
            pivot_row_indices, nb = find_min_limit_ratio_row(result_array[step_counter], pivot_column_id)
            step_counter -= 1


            return columns, data, dash.no_update, dash.no_update, result_array[step_counter], step_counter, dash.no_update, [pivot_column_id], [pivot_row_indices]



    return columns, data, dash.no_update, dash.no_update, dash.no_update, step_counter, dash.no_update, [], []


if __name__ == '__main__':
    app.run_server(debug=True)


