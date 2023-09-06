
import dash
from dash import dcc
from dash import html
import plotly.express as px
import numpy as np
#from scipy.optimize import bisect
import sympy as sp

from optimization import bisection

#Definir la App
app = dash.Dash(__name__)

#Definir el layout del app

app.layout = html.Div(
    [
        html.Div(
            [

            ]
        ),
        html.Div(
            [

            ]
        ),
        html.H1("Metodo biseccion por Johny Marin"),
        dcc.Input(id="function", placeholder="ingrese la funcion"),
        dcc.Input(id="a", placeholder="ingrese limite inferior"),
        dcc.Input(id="b", placeholder="ingrese limite superior"),
        dcc.Graph(id="graph"),
        html.Table(id="table"),
    ]

)

#Definir el callbacks
@app.callback(
    dash.dependencies.Output("graph", "figure"),
    dash.dependencies.Output("table", "children"),
    dash.dependencies.Input("function", "value"),
    dash.dependencies.Input("a", "value"),
    dash.dependencies.Input("b", "value"),
)

def plot_table(function, a, b):

    if not function or not a or not b:
        return dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
    except Exception as e:
        return dash.no_update, html.P(f"Error: {e}")

    try:
        a = float(a)
        b = float(b)
    except ValueError:
        return dash.no_update, html.P("error: invalid limit values")

    #Solve the equation using the bisection method
    try:
        x_solution, calculated_rows =  bisection(lambda x: f(x), a, b)
    except ValueError as e:
        return dash.no_update, html.P(f"Error: {e}")



    #plot the functions in the function
    x_vals = np.linspace(a, b, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo de la biseccion")

    #Create the table
    table = html.Table([
        html.Tr([
            html.Th("i"),
            html.Th("xl"),
            html.Th("xu"),
            html.Th("xr"),
            html.Th("f(xu)"),
            html.Th("f(xl)"),
            html.Th("f(xr)"),
            html.Th("f(xl)*f(xr)"),
            html.Th("error"),
        ]),
        *[
            html.Tr([
                html.Td(f"{val: 06.6f}") for val in row
            ]) for row in calculated_rows
        ]
    ])

    return fig, table



if __name__ == '__main__':
    app.run_server(debug=True)
