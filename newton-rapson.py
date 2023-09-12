import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sympy as sp


def gradient_descent(f, fprime, xi, learning_rate=0.1, max_iterations=100, tolerance=1e-3):
    calculated_rows = []
    x = xi

    for iteration in range(max_iterations):
        f_x = f(x)
        f_prime_x = fprime(x)
        d = abs(0 - f_x)

        calculated_rows.append((
            iteration,
            x,
            f_x,
            f_prime_x,
            d,
        ))

        if d < tolerance:
            break

        gradient_descent_step = x - learning_rate * f_prime_x
        x = gradient_descent_step

    return x, calculated_rows


# Define the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        html.H1("Metodo de Descenso de Gradiente por Johny Marin"),
        dcc.Input(id="equation", placeholder="Ingrese la funcion"),
        dcc.Input(id="xi", placeholder="Ingrese xi"),
        dcc.Graph(id="graph"),
        dcc.Graph(id="error-graph"),
        html.Table(id="table"),
    ]
)


# Define the callback function
@app.callback(
    [dash.dependencies.Output("graph", "figure"),
     dash.dependencies.Output("error-graph", "figure"),
     dash.dependencies.Output("table", "children")],
    [dash.dependencies.Input("equation", "value"),
     dash.dependencies.Input("xi", "value")]
)
def plot_table(function, xi):
    if not function or not xi:
        return dash.no_update, dash.no_update, dash.no_update
    x = sp.Symbol('x')

    try:
        f = sp.lambdify(x, function, 'numpy')
        function_prime = function.diff(x)
        fprima = sp.lambdify(x, function_prime, 'numpy')
    except Exception as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    try:
        xi = float(xi)
    except ValueError:
        return dash.no_update, dash.no_update, html.P("Error: Valor inicial no válido")

    # Solve for the maximum using gradient descent
    try:
        max_x, calculated_rows_max = gradient_descent(lambda x: -f(x), lambda x: -fprima(x), xi)
    except ValueError as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    # Solve for the minimum using gradient descent
    try:
        min_x, calculated_rows_min = gradient_descent(lambda x: f(x), lambda x: fprima(x), xi)
    except ValueError as e:
        return dash.no_update, dash.no_update, html.P(f"Error: {e}")

    # Create a list to store the error values
    error_values_max = [row[-1] for row in calculated_rows_max]
    error_values_min = [row[-1] for row in calculated_rows_min]

    error_fig_max = go.Figure()
    error_fig_max.add_trace(go.Scatter(x=list(range(len(error_values_max))), y=error_values_max,
                                       mode="lines+markers", name="Error (Max)"))
    error_fig_max.update_layout(title="Error in each Iteration (Max)", xaxis_title="Iteration", yaxis_title="Error")

    error_fig_min = go.Figure()
    error_fig_min.add_trace(go.Scatter(x=list(range(len(error_values_min))), y=error_values_min,
                                       mode="lines+markers", name="Error (Min)"))
    error_fig_min.update_layout(title="Error in each Iteration (Min)", xaxis_title="Iteration", yaxis_title="Error")

    # Plot the functions
    x_vals = np.linspace(xi - 10, xi + 10, 100)
    fig = px.line(x=x_vals, y=f(x_vals))
    fig.update_layout(title="Metodo de Descenso de Gradiente")

    # Create the table
    table = html.Table([
        html.Tr([
            html.Th("i"),
            html.Th("x"),
            html.Th("f(x)"),
            html.Th("f'(x)"),
            html.Th("error"),
        ]),
        *[
            html.Tr([
                html.Td(f"{val: 06.6f}") for val in row
            ]) for row in calculated_rows_max
        ],
        *[
            html.Tr([
                html.Td(f"{val: 06.6f}") for val in row
            ]) for row in calculated_rows_min
        ]
    ])

    return fig, [error_fig_max, error_fig_min], table


if __name__ == '__main__':
    app.run_server(debug=True)
