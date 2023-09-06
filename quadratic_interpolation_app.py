
import dash
from dash import dcc
from dash import html
import plotly.express as px
import numpy as np
import sympy as sp


def quadratic_interpolation(f, option, x0, x1, x2, max_iterations=100, tolerance=1e-6):
    #Evaluate function values at x0, x1 and x2
    x_values = [x0, x1, x2]
    calculated_rows = []
    factor = -1 if option == "minimum" else 1


    for iteration in range(max_iterations):
        f_values = [f(x) for x in x_values]


        if option == "minimum":
            idx = f_values.index(min(f_values))
        elif option == "maximum":
            idx = f_values.index(max(f_values))
        else:
            raise ValueError("Invalid option selected.")

        x_extreme = x_values[idx]
        y_extreme = f(x_extreme)

        x_new = (
                        f_values[0]*(x_values[1]**2-x_values[2]**2)
                        +f_values[1]*(x_values[2]**2-x_values[0]**2)
                        +f_values[2]*(x_values[0]**2-x_values[1]**2)
                )/(
                2 * f_values[0] * (x_values[1] - x_values[2])
                + 2 * f_values[1] * (x_values[2] - x_values[0])
                + 2*f_values[2] * (x_values[0] - x_values[1])
        )
        y_new = f(x_new)



        calculated_rows.append((
            iteration,
            x_values[0],
            f_values[0],
            x_values[1],
            f_values[1],
            x_values[2],
            f_values[2],
            x_new,
            y_new,
            x_extreme,
            y_extreme,
        ))

        if abs(x_new - x_extreme) < tolerance:
            break


        x_values.append(x_new)
        x_values.sort()
        if ( (  x_new - x_extreme) * ( y_new - y_extreme  ) * factor  ) > 0:
            x_values = x_values[-3:]
        else:
            x_values =  x_values[:3]

        

    return (x_extreme, y_extreme), calculated_rows


#Definir la App
app = dash.Dash(__name__)

#Definir el layout del app



radio_options = [
    {"label": "Minimo", "value": "minimum"},
    {"label": "Maximo", "value": "maximum"},
    {"label": "Raiz", "value": "root"},
]
app.layout = html.Div(
    [

        html.H1("Metodo Interpolación Cuadratica por Johny Marin"),
        dcc.Input(id="equation", placeholder="ingrese la funcion"),
        dcc.Input(id="x0", placeholder="ingrese x0"),
        dcc.Input(id="x1", placeholder="ingrese x1"),
        dcc.Input(id="x2", placeholder="ingrese x2"),
        dcc.RadioItems(id="radio-group", options=radio_options, value="minimum"),
        dcc.Graph(id="graph"),
        html.Table(id="table"),
    ]

)

#Definir el callbacks
@app.callback(
    [dash.dependencies.Output("graph", "figure"),
    dash.dependencies.Output("table", "children"),],
   [ dash.dependencies.Input("equation", "value"),
    dash.dependencies.Input("radio-group", "value"),
    dash.dependencies.Input("x0", "value"),
    dash.dependencies.Input("x1", "value"),
    dash.dependencies.Input("x2", "value"),]
)

def plot_table(function, option, x0, x1, x2):

    if not function or not x0 or not x1 or not x2:
        return dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
    except Exception as e:
        return dash.no_update, html.P(f"Error: {e}")

    try:

        x0 = float(x0)
        x1 = float(x1)
        x2 = float(x2)
    except ValueError:
        return dash.no_update, html.P("error: invalid initial values")

    #Solve the equation using the quadratic interpolation method
    try:
        x_solution, calculated_rows =  quadratic_interpolation(lambda x: f(x), option, x0, x1, x2)
    except ValueError as e:
        return dash.no_update, html.P(f"Error: {e}")



    #plot the functions in the function
    x_vals = np.linspace(x0, x2, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo interpolacion cuadratica")

    #Create the table
    table = html.Table([
        html.Tr([
            html.Th("i"),
            html.Th("x0"),
            html.Th("f(x0)"),
            html.Th("x1"),
            html.Th("f(x1)"),
            html.Th("x2"),
            html.Th("f(x2)"),
            html.Th("x3"),
            html.Th("f(x3)"),
            html.Th("x_extreme"),
            html.Th("f(x_extreme)"),
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
