
import dash
import scipy.constants
from dash import dcc
from dash import html
import plotly.express as px
import numpy as np
import sympy as sp

phi = scipy.constants.golden_ratio
phi = (np.sqrt(5)-1.0)/2.0
def golden_section_search(f, xl, xu,  max_iterations=5, tolerance=1e-3):


    calculated_rows = []


    for iteration in range(max_iterations):
        d = phi * (xu - xl)
        x1 = xl + d
        x2 = xu - d
        f_x1 = f(x1)
        f_x2 = f(x2)


        calculated_rows.append((
            iteration,
            xl,
            f(xl),
            xu,
            f(xu),
            x1,
            f_x1,
            x2,
            f_x2,
            d,
        ))

        if f_x1 < f_x2 :
            xl = xl
            xu = x1
        else:
            xu = xu
            xl = x2

        if d < tolerance:
            break
    return (xl, xu), calculated_rows


#Definir la App
app = dash.Dash(__name__)

#Definir el layout del app




app.layout = html.Div(
    [

        html.H1("Metodo Seccion Dorada por Johny Marin"),
        dcc.Input(id="equation", placeholder="ingrese la funcion"),
        dcc.Input(id="xl", placeholder="ingrese xl"),
        dcc.Input(id="xu", placeholder="ingrese xu"),
        dcc.Graph(id="graph"),
        html.Table(id="table"),
    ]

)

#Definir el callbacks
@app.callback(
    [dash.dependencies.Output("graph", "figure"),
    dash.dependencies.Output("table", "children"),],
   [ dash.dependencies.Input("equation", "value"),
    dash.dependencies.Input("xl", "value"),
    dash.dependencies.Input("xu", "value"),]
)

def plot_table(function, xl, xu):

    if not function or not xl or not xu:
        return dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
    except Exception as e:
        return dash.no_update, html.P(f"Error: {e}")

    try:

        xl = float(xl)
        xu = float(xu)
    except ValueError:
        return dash.no_update, html.P("error: invalid initial values")

    #Solve the equation using the quadratic interpolation method
    try:
        x_solution, calculated_rows =  golden_section_search(lambda x: f(x),  xl, xu)
    except ValueError as e:
        return dash.no_update, html.P(f"Error: {e}")



    #plot the functions in the function
    x_vals = np.linspace(xl, xu, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo seccion dorada")

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

    return fig, table



if __name__ == '__main__':
    app.run_server(debug=True)
