
import dash
import scipy.constants
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp


def newton_raphson( f, fprime, fprime2,  xi,  max_iterations=100, tolerance=1e-3 ):

    calculated_rows = []
    x = xi

    xu = xi+1
    xl = xi-1

    for iteration in range(max_iterations):

        f_x = f(x)
        f_prime_x = fprime(x)
        f_double_prime_x = fprime2(x)
        d = abs(0 - f_x)

        calculated_rows.append((
            iteration,
            x,
            f_x,
            f_prime_x,
            f_double_prime_x,
            d,
        ))

        if f_x < 0:
            xl = x
        else:
            xu = x


        if d < tolerance:
            break

        newton_raphson_step = x - f_x/f_prime_x
        x =  newton_raphson_step
    return (xl, xu), calculated_rows


#Definir la App
app = dash.Dash(__name__)

#Definir el layout del app




app.layout = html.Div(
    [

        html.H1("Metodo Newton  por Johny Marin"),
        dcc.Input(id="equation", placeholder="ingrese la funcion"),
        dcc.Input(id="xi", placeholder="ingrese xi"),
        dcc.Graph(id="graph"),
        dcc.Graph(id="error-graph"),
        html.Table(id="table"),
    ]

)

#Definir el callbacks
@app.callback(
    [dash.dependencies.Output("graph", "figure"),
    dash.dependencies.Output("error-graph", "figure"),
    dash.dependencies.Output("table", "children"),],
   [ dash.dependencies.Input("equation", "value"),
    dash.dependencies.Input("xi", "value"),]
)

def plot_table(function, xi):

    if not function or not xi :
        return dash.no_update, dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
        function_prime = function.diff(x)
        fprima = sp.lambdify(x, function_prime, 'numpy')
        function_double_prime = function_prime.diff(x)
        fprima2 = sp.lambdify(x, function_double_prime, 'numpy')
    except Exception as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")


    try:

        xi = float(xi)
    except ValueError:
        return dash.no_update, dash.no_update, html.P("error: invalid initial values")

    #Solve the equation using the quadratic interpolation method
    try:
        x_solution, calculated_rows =  newton_raphson(lambda x: f(x), lambda x: fprima(x), lambda x: fprima2(x), xi)
    except ValueError as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    # Create a list to store the error values
    error_values = [row[-1] for row in calculated_rows]

    error_fig = go.Figure()
    error_fig.add_trace(
        go.Scatter(x=list(range(len(error_values))), y=error_values, mode="lines+markers", name="Error"))
    error_fig.update_layout(title="Error in each Iteration", xaxis_title="Iteration", yaxis_title="Error")

    #plot the functions in the function
    x_vals = np.linspace(xi-10, xi+10, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo  newton raphson")

    #Create the table
    table = html.Table([
        html.Tr([
            html.Th("i"),
            html.Th("xl"),
            html.Th("f(xl)"),
            html.Th("xu"),
            html.Th("f(xu)"),
            html.Th("x1"),
            html.Th("f(x1)"),
            html.Th("x2"),
            html.Th("f(x2)"),
            html.Th("error"),
        ]),
        *[
            html.Tr([
                html.Td(f"{val: 06.6f}") for val in row
            ]) for row in calculated_rows
        ]
    ])

    return fig, error_fig, table

if __name__ == '__main__':
    app.run_server(debug=True)
