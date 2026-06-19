"""
tabs/contextoproblema.py
========================
Pestaña 1 — Contexto del Problema.
Describe el impacto operativo y comercial del deterioro de
micromedidores en Triple A / Barranquilla.
"""

from dash import html
import dash_bootstrap_components as dbc

# ── Estilos compartidos ───────────────────────────────────────────────────────
_TITLE = {
    "color": "#ffffff",
    "fontWeight": "800",
    "fontSize": "1.75rem",
    "borderLeft": "6px solid #E07B2A",
    "paddingLeft": "16px",
    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
}
_SUBTITLE = {
    "color": "#94a3b8",
    "fontSize": "0.95rem",
    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
    "marginBottom": "2rem",
}
_TEXT = {
    "color": "#cbd5e1",
    "fontSize": "0.93rem",
    "lineHeight": "1.9",
    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
    "textAlign": "justify",
    "marginBottom": "1rem",
}
_CARD = {
    "backgroundColor": "#0D1E35",
    "border": "1px solid #1e3a5f",
    "borderRadius": "14px",
    "height": "100%",
}
_CARD_HEADER = {
    "backgroundColor": "#091626",
    "border": "none",
    "borderRadius": "14px 14px 0 0",
    "padding": "1rem 1.4rem 0.5rem",
}

# ── KPI Cards ─────────────────────────────────────────────────────────────────
KPIS = [
    {"valor": "~397K",  "label": "Medidores evaluados",        "color": "#3B82F6"},
    {"valor": "87.65%", "label": "Requieren cambio prioritario","color": "#EF4444"},
    {"valor": "12–35%", "label": "Pérdida de ingresos por ANC","color": "#E07B2A"},
    {"valor": "US$ M",  "label": "Impacto anual estimado",     "color": "#10B981"},
]

# ── Fases del proceso ─────────────────────────────────────────────────────────
FASES = [
    {
        "num": "01",
        "titulo": "Reactivo (pasado)",
        "texto": (
            "El cambio solo se ejecutaba cuando el equipo se detenía por completo o "
            "cuando un operario reportaba una anomalía visible en terreno. "
            "Alta cantidad de agua no facturada y costos de emergencia elevados."
        ),
        "color": "#EF4444",
        "icono": "⚠️",
    },
    {
        "num": "02",
        "titulo": "Preventivo por Edad (actual parcial)",
        "texto": (
            "Se reemplazan equipos al cumplir un ciclo de años predeterminado. "
            "Mejora respecto al enfoque reactivo, pero ignora la diversidad de "
            "tecnologías, marcas y entornos hidráulicos que aceleran o retrasan el deterioro."
        ),
        "color": "#E07B2A",
        "icono": "🕐",
    },
    {
        "num": "03",
        "titulo": "Predictivo con ML (propuesto)",
        "texto": (
            "Un modelo de clasificación binaria analiza edad, consumo promedio, "
            "deterioro, tecnología y marca para determinar científicamente la "
            "prioridad de cambio. Permite enfocar las cuadrillas en los medidores "
            "de mayor riesgo antes del fallo total."
        ),
        "color": "#10B981",
        "icono": "🤖",
    },
]

# ── Variables del modelo ───────────────────────────────────────────────────────
VARIABLES = [
    {"nombre": "Edad del Medidor",               "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Deterioro del Consumo",          "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Promedio de Consumo Real",       "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Lectura Acumulada",              "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Score de Priorización Asignado", "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Último Consumo Facturado",       "rol": "Predictor",  "tipo": "Numérica"},
    {"nombre": "Tecnología",                     "rol": "Predictor",  "tipo": "Categórica"},
    {"nombre": "Marca del Medidor",              "rol": "Predictor",  "tipo": "Categórica"},
    {"nombre": "Diámetro",                       "rol": "Predictor",  "tipo": "Categórica"},
    {"nombre": "Último Método Facturado",        "rol": "Predictor",  "tipo": "Categórica"},
    {"nombre": "prioridad_cambio",               "rol": "🎯 Target",  "tipo": "Binaria (0/1)"},
]


def layout():
    return dbc.Container([

        # ── Título ────────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.H1("Contexto del Problema", style=_TITLE),
                html.P(
                    "Predicción del deterioro y prioridad de cambio de micromedidores "
                    "de agua — Triple A · Barranquilla, Colombia",
                    style=_SUBTITLE,
                ),
                html.Hr(style={"borderColor": "#1e3a5f"}),
            ])
        ], className="mt-4"),

        # ── KPI Cards ─────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H2(k["valor"], style={
                        "color": k["color"], "fontWeight": "800",
                        "textAlign": "center",
                        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                    }),
                    html.P(k["label"], style={
                        "textAlign": "center", "color": "#94a3b8",
                        "fontSize": "0.82rem", "marginBottom": "0",
                        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                    }),
                ]), style=_CARD),
                md=3, className="mb-4",
            )
            for k in KPIS
        ]),

        html.Hr(style={"borderColor": "#1e3a5f"}),

        # ── Descripción del problema ──────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.H4("¿Por qué predecir el deterioro de medidores?", style={
                    "color": "#ffffff",
                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                    "fontWeight": "700", "marginBottom": "1rem",
                }),
                html.P(
                    "El deterioro y fallo de los medidores de acueducto representa uno de los "
                    "principales desafíos operativos y comerciales para las empresas prestadoras "
                    "de servicios públicos en la ciudad de Barranquilla. Predecir y detectar "
                    "este desgaste antes de que se presente un fallo total es fundamental para "
                    "minimizar el Agua No Contabilizada (ANC), garantizar un cobro justo a los "
                    "usuarios, proteger los ingresos de la compañía y optimizar el despliegue "
                    "de las cuadrillas de mantenimiento.",
                    style=_TEXT,
                ),
                html.P(
                    "Una de las características que dificultan la detección temprana es que "
                    "la submedición —cuando el equipo registra menos agua de la real— es un "
                    "proceso silencioso. Puede confundirse con una disminución legítima en los "
                    "hábitos de consumo o con variaciones en el método de facturación. "
                    "Solo un análisis multivariado, combinando edad, consumo histórico, "
                    "tecnología y marca, permite separar ambos fenómenos de forma confiable.",
                    style=_TEXT,
                ),
            ], md=8),

            dbc.Col([
                dbc.Card(dbc.CardBody([
                    html.H5("Impacto del Agua No Facturada", style={
                        "color": "#E07B2A", "fontWeight": "700",
                        "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                        "marginBottom": "1rem",
                    }),
                    html.Ul([
                        html.Li("Pérdida directa de ingresos por m³ subregistrado.", style=_TEXT),
                        html.Li("Desbalance en los índices de micromedición.", style=_TEXT),
                        html.Li("Usuarios pagan menos de lo que realmente consumen.", style=_TEXT),
                        html.Li("Sobrecarga de la red por consumo no reportado.", style=_TEXT),
                        html.Li("Ineficiencia en la gestión de activos físicos.", style=_TEXT),
                    ], style={"paddingLeft": "1.2rem"}),
                ]), style={**_CARD, "borderLeft": "4px solid #E07B2A"}),
            ], md=4),
        ], className="mb-4"),

        html.Hr(style={"borderColor": "#1e3a5f"}),

        # ── Evolución del enfoque ─────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.H4("Evolución del enfoque de gestión", style={
                    "color": "#ffffff",
                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                    "fontWeight": "700", "marginBottom": "1.5rem",
                }),
            ])
        ]),

        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Div(style={
                            "width": "5px",
                            "backgroundColor": fase["color"],
                            "borderRadius": "4px",
                            "flexShrink": "0",
                            "marginRight": "1.2rem",
                            "alignSelf": "stretch",
                        }),
                        html.Div([
                            html.Div([
                                html.Span(fase["icono"] + " ", style={"fontSize": "1.1rem"}),
                                html.Span(fase["num"], style={
                                    "color": fase["color"], "fontWeight": "800",
                                    "fontSize": "0.85rem", "marginRight": "0.5rem",
                                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                                }),
                                html.Span(fase["titulo"], style={
                                    "color": "#ffffff", "fontWeight": "700",
                                    "fontSize": "0.95rem",
                                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                                }),
                            ], style={"marginBottom": "0.5rem"}),
                            html.P(fase["texto"], style={**_TEXT, "marginBottom": "0"}),
                        ]),
                    ], style={
                        "display": "flex",
                        "padding": "1.2rem",
                        "backgroundColor": "#0D1E35",
                        "border": "1px solid #1e3a5f",
                        "borderRadius": "12px",
                        "marginBottom": "1rem",
                    }),
                ])
                for fase in FASES
            ])
        ], className="mb-4"),

        html.Hr(style={"borderColor": "#1e3a5f"}),

        # ── Variables del modelo ───────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.H4("Variables del Dataset (Historico.xlsx)", style={
                    "color": "#ffffff",
                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                    "fontWeight": "700", "marginBottom": "1rem",
                }),
                dbc.Table(
                    [
                        html.Thead(
                            html.Tr([
                                html.Th("Variable", style={"color": "#ffffff", "backgroundColor": "#091626", "fontFamily": "'Inter', 'Segoe UI', sans-serif"}),
                                html.Th("Rol", style={"color": "#ffffff", "backgroundColor": "#091626", "fontFamily": "'Inter', 'Segoe UI', sans-serif"}),
                                html.Th("Tipo", style={"color": "#ffffff", "backgroundColor": "#091626", "fontFamily": "'Inter', 'Segoe UI', sans-serif"}),
                            ])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td(v["nombre"], style={
                                    "color": "#C0392B" if v["rol"] == "🎯 Target" else "#1e293b",
                                    "fontWeight": "700" if v["rol"] == "🎯 Target" else "500",
                                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                                    "fontSize": "0.88rem",
                                }),
                                html.Td(v["rol"], style={
                                    "color": "#16a34a" if v["rol"] == "🎯 Target" else "#334155",
                                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                                    "fontSize": "0.85rem",
                                }),
                                html.Td(v["tipo"], style={
                                    "color": "#1d4ed8",
                                    "fontFamily": "'Inter', 'Segoe UI', sans-serif",
                                    "fontSize": "0.85rem",
                                }),
                            ], style={
                                "backgroundColor": "#f8fafc" if i % 2 == 0 else "#f1f5f9",
                                "borderBottom": "1px solid #e2e8f0",
                            })
                            for i, v in enumerate(VARIABLES)
                        ]),
                    ],
                    bordered=False,
                    responsive=True,
                    style={"borderRadius": "12px", "overflow": "hidden", "border": "1px solid #1e3a5f"},
                ),
            ])
        ], className="mb-5"),

    ], fluid=True, style={"padding": "2rem 3rem", "backgroundColor": "#060F1C"})
