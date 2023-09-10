
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp


def regula_falsi(f, xl, xu,  max_iterations=100, tolerance=1e-6):
    #Evaluate function values at x0, x1 and x2
    if (f(xl)*f(xu)) >= 0:
        raise ValueError ("Function must have opposite sign values")

    calculated_rows = []
    x_old = 0
    for iteration in range(max_iterations):
        fl = f(xl)
        fu = f(xu)

        x_new = (xl * fu - xu * fl)/( fu - fl )
        fx_new =f(x_new)


        calculated_rows.append((
            iteration,
            xl,
            fl,
            xu,
            fu,
            x_new,
            fx_new,
            x_new - x_old,
        ))

        if abs(x_new - x_old) < tolerance or abs(x_new) < tolerance :
            break

        x_old = x_new

        if (fl * fx_new > 0):
            xl = x_new
        elif (fl * fx_new < 0):
            xu = x_new
        

    return (x_new, fx_new), calculated_rows


#Definir la App
app = dash.Dash(__name__)

#Definir el layout del app




app.layout = html.Div(
    [

        html.H1("Metodo Falsa pocision por Johny Marin"),
        dcc.Input(id="equation", placeholder="ingrese la funcion"),
        dcc.Input(id="xl", placeholder="ingrese xl"),
        dcc.Input(id="xu", placeholder="ingrese xu"),
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
    dash.dependencies.Input("xl", "value"),
    dash.dependencies.Input("xu", "value"),]
)

def plot_table(function, xl, xu):

    if not function or not xl or not xu:
        return dash.no_update, dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
    except Exception as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    try:

        xl = float(xl)
        xu = float(xu)
    except ValueError:
        return dash.no_update, dash.no_update, html.P("error: invalid initial values")

    #Solve the equation using the quadratic interpolation method
    try:
        x_solution, calculated_rows =  regula_falsi(lambda x: f(x),  xl, xu)
    except ValueError as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    # Create a list to store the error values
    error_values = [row[-1] for row in calculated_rows]

    error_fig = go.Figure()
    error_fig.add_trace(
        go.Scatter(x=list(range(len(error_values))), y=error_values, mode="lines+markers", name="Error"))
    error_fig.update_layout(title="Error in each Iteration", xaxis_title="Iteration", yaxis_title="Error")

    #plot the functions in the function
    x_vals = np.linspace(xl, xu, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo interpolacion cuadratica")

    #Create the table
    table = html.Table([
        html.Tr([
            html.Th("i"),
            html.Th("xl"),
            html.Th("f(xl)"),
            html.Th("xu"),
            html.Th("f(xu)"),
            html.Th("xr"),
            html.Th("f(xr)"),
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
