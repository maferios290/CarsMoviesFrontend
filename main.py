import dash
from dash import dcc, html, dash_table, Input, Output, State
import requests

app = dash.Dash(__name__)
API_BASE = "https://carsmoviesinventoryproject-production.up.railway.app/api/v1/carsmovies"

def fetch_data():
    resp = requests.get(f"{API_BASE}?page=0&size=100&sort=carMovieYear,desc")
    if resp.status_code == 200:
        return resp.json().get("Movies", [])
    return []

app.layout = html.Div(style={
        "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        "backgroundColor": "#f0f2f5",
        "minHeight": "100vh",
        "padding": "40px"
    }, children=[
    html.Div(style={
        "maxWidth": "900px",
        "margin": "auto",
        "backgroundColor": "white",
        "borderRadius": "10px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.1)",
        "padding": "30px"
    }, children=[
        html.H1("🚗 Cars Movies Dashboard", style={
            "textAlign": "center",
            "color": "#003366",
            "marginBottom": "40px"
        }),

        dash_table.DataTable(
            id="movies-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Name", "id": "carMovieName"},
                {"name": "Year", "id": "carMovieYear", "type": "numeric"},
                {"name": "Duration (min)", "id": "duration", "type": "numeric"},
            ],
            data=fetch_data(),
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "8px",
                "fontSize": "14px",
                "whiteSpace": "normal",
                "height": "auto"
            },
            style_header={
                "backgroundColor": "#003366",
                "color": "white",
                "fontWeight": "bold",
                "fontSize": "16px"
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f9f9f9"},
                {"if": {"state": "active"}, "backgroundColor": "#d0e1f9"},
            ],
            page_size=10,
            row_selectable="single",
            style_as_list_view=True,
        ),

        html.Div(style={"marginTop": "40px"}, children=[
            html.H3("Add / Update Movie", style={"color": "#003366", "marginBottom": "20px"}),
            html.Div([
                dcc.Input(id="input-id", type="hidden"),

                dcc.Input(
                    id="input-name", type="text", placeholder="Movie Name",
                    style={
                        "width": "40%",
                        "padding": "10px",
                        "marginRight": "15px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "fontSize": "14px"
                    }
                ),
                dcc.Input(
                    id="input-year", type="number", placeholder="Year",
                    style={
                        "width": "15%",
                        "padding": "10px",
                        "marginRight": "15px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "fontSize": "14px"
                    }
                ),
                dcc.Input(
                    id="input-duration", type="number", placeholder="Duration (min)",
                    style={
                        "width": "15%",
                        "padding": "10px",
                        "marginRight": "15px",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc",
                        "fontSize": "14px"
                    }
                ),

                html.Button("Save", id="btn-save", n_clicks=0, style={
                    "backgroundColor": "#007BFF",
                    "color": "white",
                    "border": "none",
                    "padding": "12px 25px",
                    "borderRadius": "5px",
                    "fontWeight": "bold",
                    "cursor": "pointer",
                    "transition": "background-color 0.3s ease"
                }),

                html.Button("Delete", id="btn-delete", n_clicks=0, style={
                    "backgroundColor": "#dc3545",
                    "color": "white",
                    "border": "none",
                    "padding": "12px 25px",
                    "borderRadius": "5px",
                    "marginLeft": "10px",
                    "fontWeight": "bold",
                    "cursor": "pointer",
                    "transition": "background-color 0.3s ease"
                }),

                html.Button("Clear", id="btn-clear", n_clicks=0, style={
                    "backgroundColor": "#6c757d",
                    "color": "white",
                    "border": "none",
                    "padding": "12px 25px",
                    "borderRadius": "5px",
                    "marginLeft": "10px",
                    "fontWeight": "bold",
                    "cursor": "pointer",
                    "transition": "background-color 0.3s ease"
                }),
            ], style={"display": "flex", "alignItems": "center"}),
        ]),

        html.Div(id="message", style={"marginTop": "20px", "fontWeight": "bold"}),

    ])
])

# Callback para llenar inputs al seleccionar fila
@app.callback(
    Output("input-id", "value"),
    Output("input-name", "value"),
    Output("input-year", "value"),
    Output("input-duration", "value"),
    Input("movies-table", "selected_rows"),
    State("movies-table", "data")
)
def fill_inputs(selected_rows, data):
    if selected_rows and len(selected_rows) > 0:
        row = data[selected_rows[0]]
        return row.get("id"), row.get("carMovieName"), row.get("carMovieYear"), row.get("duration")
    return "", "", "", ""

# Callback para guardar (crear o actualizar)
@app.callback(
    Output("message", "children"),
    Output("movies-table", "data"),
    Input("btn-save", "n_clicks"),
    State("input-id", "value"),
    State("input-name", "value"),
    State("input-year", "value"),
    State("input-duration", "value"),
    prevent_initial_call=True
)
def save_movie(n_clicks, movie_id, name, year, duration):
    if not name or not year or not duration:
        return "⚠️ Por favor, completa todos los campos.", dash.no_update

    movie_payload = {
        "carMovieName": name,
        "carMovieYear": int(year),
        "duration": int(duration)
    }

    headers = {"Content-Type": "application/json"}

    if movie_id:
        # Actualizar (PUT)
        response = requests.put(f"{API_BASE}/{movie_id}", json=movie_payload, headers=headers)
        if response.status_code == 200:
            msg = "✔️ Película actualizada con éxito."
        else:
            msg = f"❌ Error al actualizar: {response.text}"
    else:
        # Crear (POST)
        response = requests.post(API_BASE, json=movie_payload, headers=headers)
        if response.status_code == 201:
            msg = "✔️ Película creada con éxito."
        else:
            msg = f"❌ Error al crear: {response.text}"

    # Refrescar datos
    data = fetch_data()
    return msg, data

# Callback para eliminar película
@app.callback(
    Output("message", "children"),
    Output("movies-table", "data"),
    Output("input-id", "value"),
    Output("input-name", "value"),
    Output("input-year", "value"),
    Output("input-duration", "value"),
    Input("btn-delete", "n_clicks"),
    State("input-id", "value"),
    prevent_initial_call=True
)
def delete_movie(n_clicks, movie_id):
    if not movie_id:
        return "⚠️ Selecciona una película para eliminar.", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    response = requests.delete(f"{API_BASE}/{movie_id}")

    if response.status_code == 204:
        msg = "✔️ Película eliminada con éxito."
        data = fetch_data()
        # Limpiar inputs
        return msg, data, "", "", "", ""
    else:
        return f"❌ Error al eliminar: {response.text}", dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback para limpiar inputs
@app.callback(
    Output("input-id", "value"),
    Output("input-name", "value"),
    Output("input-year", "value"),
    Output("input-duration", "value"),
    Output("message", "children"),
    Input("btn-clear", "n_clicks"),
    prevent_initial_call=True
)
def clear_inputs(n_clicks):
    return "", "", "", "", ""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")


