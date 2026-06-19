"""
app.py
======
Punto de entrada principal del dashboard de Prediccion de Deterioro de
Micromedidores — Triple A, Barranquilla.

Arquitectura modular: cada pestaña es un modulo independiente en /tabs.

Para ejecutar:
    python app.py

Para entrenamiento previo del modelo:
    python model/train_model.py
"""

import sys
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html

# Asegura que /tabs y /model sean importables desde cualquier CWD
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Importar layouts de cada pestana
from tabs.contextoproblema import layout as layout_contexto
from tabs.eda import layout as layout_eda
from tabs.metricasmodelo import layout as layout_metricas
from tabs.prediccionmodelo import layout as layout_prediccion
from tabs.prediccionmodelo import register_callbacks

# ── Inicializacion de la app ──────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Deterioro de Micromedidores — Triple A"
server = app.server  # Para Gunicorn en produccion

# ── Registro de callbacks de pestanas ────────────────────────────────────────
register_callbacks(app)

# ── IDs de tabs ───────────────────────────────────────────────────────────────
TABS = [
    {"id": "tab-contexto",  "label": "Contexto del Problema", "icon": "🏢"},
    {"id": "tab-eda",       "label": "Analisis Exploratorio",  "icon": "📊"},
    {"id": "tab-metricas",  "label": "Metricas del Modelo",    "icon": "📈"},
    {"id": "tab-prediccion","label": "Prediccion",             "icon": "🔮"},
]

# ── Navbar ────────────────────────────────────────────────────────────────────
navbar = dbc.Navbar(
    dbc.Container([
        # Logo / brand
        html.A(
            dbc.Row([
                dbc.Col(html.Span("💧", style={"fontSize": "1.4rem", "marginRight": "0.5rem"})),
                dbc.Col(dbc.NavbarBrand(
                    "Prediccion de Deterioro de Micromedidores",
                    className="ms-1",
                    style={
                        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                        "fontWeight": "700",
                        "fontSize": "0.95rem",
                        "color": "#ffffff",
                    },
                )),
            ], align="center", className="g-0"),
            href="#",
            style={"textDecoration": "none"},
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(
                    f"{t['icon']} {t['label']}",
                    id=f"nav-{t['id']}",
                    href="#",
                    active=False,
                    style={
                        "color": "#cbd5e1",
                        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                        "fontSize": "0.85rem",
                        "padding": "0.5rem 0.8rem",
                    },
                ))
                for t in TABS
            ], navbar=True, className="ms-auto"),
            id="navbar-collapse",
            navbar=True,
        ),
        # Badge de la empresa
        dbc.Badge(
            "Triple A · Barranquilla",
            color="primary",
            style={
                "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                "fontSize": "0.72rem",
                "marginLeft": "1rem",
            },
        ),
    ], fluid=True),
    color="dark",
    dark=True,
    sticky="top",
    style={
        "backgroundColor": "#060F1C",
        "borderBottom": "1px solid #1e3a5f",
        "boxShadow": "0 2px 16px rgba(0,0,0,0.5)",
    },
)

# ── Layout principal ──────────────────────────────────────────────────────────
app.layout = html.Div([
    navbar,
    dcc.Store(id="tab-activa", data="tab-contexto"),
    html.Div(id="contenido-principal"),
], style={"backgroundColor": "#060F1C", "minHeight": "100vh"})


# ── Callback: toggle navbar (responsive) ─────────────────────────────────────
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_navbar(n, is_open):
    return not is_open


# ── Callback: navegacion entre tabs ──────────────────────────────────────────
@app.callback(
    Output("tab-activa", "data"),
    [Input(f"nav-{t['id']}", "n_clicks") for t in TABS],
    prevent_initial_call=True,
)
def actualizar_tab(*args):
    from dash import ctx
    if not ctx.triggered_id:
        return "tab-contexto"
    # El id tiene forma "nav-tab-XXX", extraemos "tab-XXX"
    return ctx.triggered_id.replace("nav-", "")


# ── Callback: estilo activo de los navlinks ───────────────────────────────────
@app.callback(
    [Output(f"nav-{t['id']}", "style") for t in TABS],
    Input("tab-activa", "data"),
)
def resaltar_tab(tab_activa):
    estilos = []
    for t in TABS:
        if t["id"] == tab_activa:
            estilos.append({
                "color": "#ffffff",
                "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                "fontSize": "0.85rem",
                "padding": "0.5rem 0.8rem",
                "borderBottom": "2px solid #3B82F6",
                "fontWeight": "700",
            })
        else:
            estilos.append({
                "color": "#94a3b8",
                "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                "fontSize": "0.85rem",
                "padding": "0.5rem 0.8rem",
            })
    return estilos


# ── Callback: renderizar contenido de la tab ──────────────────────────────────
@app.callback(
    Output("contenido-principal", "children"),
    Input("tab-activa", "data"),
)
def renderizar_tab(tab_id):
    MAPA = {
        "tab-contexto":  layout_contexto,
        "tab-eda":       layout_eda,
        "tab-metricas":  layout_metricas,
        "tab-prediccion": layout_prediccion,
    }
    fn = MAPA.get(tab_id, layout_contexto)
    return fn()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
