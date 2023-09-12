import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp
import random

# Define the function to find the root using random search
def random_search(f, a, b, max_iterations=100, tolerance=1e-3):
    calculated_rows = []

    for iteration in range(max_iterations):
        x = random.uniform(a, b)
        f_x = f(x)
        d = abs(0 - f_x)

        calculated_rows.append((
            iteration,
            x,
            f_x,
            d,
        ))

        if d < tolerance:
            break

    return calculated_rows

# Define the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        html.H1("Metodo de Busqueda Aleatoria para Encontrar Raices"),
        dcc.Input(id="function", placeholder="Ingrese la funcion"),
        dcc.Input(id="a", placeholder="Ingrese limite inferior"),
        dcc.Input(id="b", placeholder="Ingrese limite superior"),
        dcc.Graph(id="graph"),
        html.Table(id="table"),
    ]
)

# Define the callback function
@app.callback(
    [dash.dependencies.Output("graph", "figure"),
     dash.dependencies.Output("table", "children")],
    [dash.dependencies.Input("function", "value"),
     dash.dependencies.Input("a", "value"),
     dash.dependencies.Input("b", "value")]
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
        return dash.no_update, html.P("Error: Valores de límite no válidos")

    # Perform random search to find the root
    try:
        calculated_rows = random_search(lambda x: f(x), a, b)
    except ValueError as e:
        return dash.no_update, html.P(f"Error: {e}")

    # Create a list to store the error values
    error_values = [row[-1] for row in calculated_rows]

    error_fig = go.Figure()
    error_fig.add_trace(go.Scatter(x=list(range(len(error_values))), y=error_values, mode="lines+markers", name="Error"))
    error_fig.update_layout(title="Error en cada iteración", xaxis_title="Iteración", yaxis_title="Error")

    # Create the table
    table = html.Table([
        html.Tr([
            html.Th("Iteración"),
            html.Th("x"),
            html.Th("f(x)"),
            html.Th("Error"),
        ]),
        *[
            html.Tr([
                html.Td(f"{val: 06.6f}") for val in row
            ]) for row in calculated_rows
        ]
    ])

    # Plot the function
    x_vals = np.linspace(a, b, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo de Busqueda Aleatoria")

    return fig, table

if __name__ == '__main__':
    app.run_server(debug=True)
