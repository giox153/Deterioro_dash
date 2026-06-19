"""
tabs/prediccionmodelo.py - Formulario corregido con rangos fijos del dominio.
"""
import json, pickle
from pathlib import Path
import pandas as pd
from dash import Input, Output, State, dcc, html, no_update
import dash_bootstrap_components as dbc

MODEL_DIR = Path(__file__).parent.parent / "model"
MODEL_PATH = MODEL_DIR / "model.pkl"
META_PATH  = MODEL_DIR / "feature_names.json"

_TITLE = {"color":"#ffffff","fontWeight":"800","fontSize":"1.75rem",
          "borderLeft":"6px solid #10B981","paddingLeft":"16px",
          "fontFamily":"'Inter','Segoe UI',sans-serif"}
_SUB   = {"color":"#94a3b8","fontSize":"0.88rem","fontFamily":"'Inter','Segoe UI',sans-serif","marginBottom":"1rem"}
_LABEL = {"color":"#94a3b8","fontSize":"0.8rem","fontFamily":"'Inter','Segoe UI',sans-serif",
          "marginBottom":"0.15rem","display":"block","marginTop":"0.8rem"}
_CARD  = {"backgroundColor":"#0D1E35","border":"1px solid #1e3a5f","borderRadius":"14px"}
_DD    = {"backgroundColor":"#091626","border":"1px solid #1e3a5f","borderRadius":"8px",
          "color":"#ffffff","fontFamily":"'Inter','Segoe UI',sans-serif","fontSize":"0.88rem"}

# Rangos FIJOS del dominio — no dependen del dataset
RANGES = {
    "Edad del Medidor":               {"min":0,   "max":35,   "val":7,   "step":1,   "suf":" años"},
    "Deterioro del Consumo":          {"min":-95, "max":40,   "val":-12, "step":1,   "suf":"%"},
    "Promedio de Consumo Real":       {"min":0,   "max":80,   "val":15,  "step":0.5, "suf":" m³"},
    "Lectura Acumulada":              {"min":0,   "max":8000, "val":900, "step":50,  "suf":" m³"},
    "Ultimo Consumo Facturado":       {"min":0,   "max":60,   "val":13,  "step":1,   "suf":" m³"},
    "Score de Priorizacion Asignado": {"min":0,   "max":100,  "val":35,  "step":1,   "suf":""},
}

def _load_meta():
    if META_PATH.exists():
        with open(META_PATH,"r",encoding="utf-8") as f:
            m = json.load(f)
            # Siempre usar rangos fijos del dominio
            m["num_ranges"] = RANGES
            return m
    return {
        "cat_options": {
            "Tecnologia": ["Mecánico","Estático"],
            "Marca del Medidor": ["ARAD","ELSTER","ITRON","SENSUS","ZENNER"],
            "Diametro": ['1/2"','3/4"','1"','1 1/2"','2"'],
            "Ultimo Metodo Facturado": ["Medido","Estimado","Promedio","Aforo"],
        },
        "num_ranges": RANGES,
    }

META = _load_meta()

def _mk_slider(sid, label, key):
    r = RANGES[key]
    mn, mx, val, step, suf = r["min"], r["max"], r["val"], r["step"], r["suf"]
    marks = {mn: {"label": f"{mn}{suf}", "style":{"color":"#64748b","fontSize":"0.72rem"}},
             mx: {"label": f"{mx}{suf}", "style":{"color":"#64748b","fontSize":"0.72rem"}}}
    return html.Div([
        html.Label(label, style=_LABEL),
        dcc.Slider(id=sid, min=mn, max=mx, step=step, value=val, marks=marks,
                   tooltip={"placement":"bottom","always_visible":True}),
    ], style={"marginBottom":"1.2rem","paddingBottom":"0.3rem"})

def layout():
    cat = META.get("cat_options", {})
    model_ok = MODEL_PATH.exists()

    def dd(sid, key):
        opts = cat.get(key, [])
        return dcc.Dropdown(id=sid,
                            options=[{"label":v,"value":v} for v in opts],
                            value=opts[0] if opts else None,
                            clearable=False, style=_DD)

    return dbc.Container([
        dbc.Row([dbc.Col([
            html.H1("Predicción en Tiempo Real", style=_TITLE),
            html.P("Ingresa las características del medidor para obtener la predicción del modelo.",style=_SUB),
            html.Hr(style={"borderColor":"#1e3a5f"}),
        ])], className="mt-4"),

        dbc.Alert([html.Strong("Modelo no disponible. "),"Ejecuta: ",html.Code("python model/train_model.py")],
                  color="warning",className="mb-4") if not model_ok else html.Div(),

        dbc.Row([
            # ── Formulario ────────────────────────────────────────────────────
            dbc.Col([
                dbc.Card(dbc.CardBody([

                    html.H6("Variables Numéricas", style={
                        "color":"#3B82F6","fontWeight":"700",
                        "fontFamily":"'Inter',sans-serif",
                        "borderBottom":"1px solid #1e3a5f",
                        "paddingBottom":"0.4rem","marginBottom":"0.5rem"}),

                    dbc.Row([
                        dbc.Col([
                            _mk_slider("pred-edad",      "Edad del Medidor (años)",        "Edad del Medidor"),
                            _mk_slider("pred-deterioro", "Deterioro del Consumo (%)",      "Deterioro del Consumo"),
                            _mk_slider("pred-promedio",  "Promedio de Consumo Real (m³)",  "Promedio de Consumo Real"),
                        ], md=6),
                        dbc.Col([
                            _mk_slider("pred-lectura",   "Lectura Acumulada (m³)",         "Lectura Acumulada"),
                            _mk_slider("pred-ultimo",    "Último Consumo Facturado (m³)",  "Ultimo Consumo Facturado"),
                            _mk_slider("pred-score",     "Score de Priorización",          "Score de Priorizacion Asignado"),
                        ], md=6),
                    ]),

                    html.Hr(style={"borderColor":"#1e3a5f","margin":"0.8rem 0"}),

                    html.H6("Variables Categóricas", style={
                        "color":"#3B82F6","fontWeight":"700",
                        "fontFamily":"'Inter',sans-serif",
                        "borderBottom":"1px solid #1e3a5f",
                        "paddingBottom":"0.4rem","marginBottom":"0.8rem"}),

                    dbc.Row([
                        dbc.Col([
                            html.Label("Tecnología", style=_LABEL),
                            dd("pred-tecnologia","Tecnologia"),
                        ], md=6, className="mb-2"),

                        dbc.Col([
                            html.Label("Diámetro", style=_LABEL),
                            dd("pred-diametro","Diametro"),
                        ], md=6, className="mb-2"),
                        dbc.Col([
                            html.Label("Último Método Facturado", style=_LABEL),
                            dd("pred-metodo","Ultimo Metodo Facturado"),
                        ], md=6, className="mb-2"),
                    ]),

                    html.Hr(style={"borderColor":"#1e3a5f","margin":"0.8rem 0"}),

                    dbc.Button("Ejecutar Predicción", id="btn-predecir",
                               color="primary", className="w-100", size="lg",
                               style={"fontFamily":"'Inter',sans-serif","fontWeight":"700",
                                      "backgroundColor":"#3B82F6","border":"none","borderRadius":"10px"},
                               disabled=not model_ok),
                ]), style=_CARD),
            ], md=7),

            # ── Resultado ─────────────────────────────────────────────────────
            dbc.Col([
                html.Div(id="resultado-prediccion", children=[
                    dbc.Card(dbc.CardBody([
                        html.Div([
                            html.Div("🔍", style={"fontSize":"3rem","textAlign":"center","marginBottom":"0.8rem"}),
                            html.H5("Esperando datos...", style={"color":"#64748b","textAlign":"center","fontFamily":"'Inter',sans-serif"}),
                            html.P("Configura los parámetros y haz clic en 'Ejecutar Predicción'.",
                                   style={"color":"#475569","textAlign":"center","fontSize":"0.85rem","fontFamily":"'Inter',sans-serif"}),
                        ]),
                    ]), style={**_CARD,"minHeight":"220px","display":"flex","alignItems":"center","justifyContent":"center"}),
                ]),

                dbc.Card(dbc.CardBody([
                    html.H6("Guía de Interpretación", style={"color":"#ffffff","fontWeight":"700","fontFamily":"'Inter',sans-serif","marginBottom":"0.8rem"}),
                    html.Div([
                        html.Span("PRIORIDAD DE CAMBIO", style={"backgroundColor":"#EF4444","color":"#fff","fontWeight":"700","padding":"0.15rem 0.5rem","borderRadius":"5px","fontSize":"0.72rem"}),
                        html.Span(" Deterioro metrológico severo. Incluir en próxima cuadrilla.",
                                  style={"color":"#94a3b8","fontSize":"0.8rem","marginLeft":"0.4rem","fontFamily":"'Inter',sans-serif"}),
                    ], style={"marginBottom":"0.6rem"}),
                    html.Div([
                        html.Span("ESTADO ÓPTIMO", style={"backgroundColor":"#10B981","color":"#fff","fontWeight":"700","padding":"0.15rem 0.5rem","borderRadius":"5px","fontSize":"0.72rem"}),
                        html.Span(" Opera en parámetros normales. No requiere intervención inmediata.",
                                  style={"color":"#94a3b8","fontSize":"0.8rem","marginLeft":"0.4rem","fontFamily":"'Inter',sans-serif"}),
                    ]),
                    html.Hr(style={"borderColor":"#1e3a5f","margin":"0.8rem 0"}),
                    html.P("Probabilidad > 0.75: alta certeza. Entre 0.40-0.75: validar en campo.",
                           style={"color":"#64748b","fontSize":"0.78rem","fontFamily":"'Inter',sans-serif","marginBottom":"0"}),
                ]), style={**_CARD,"marginTop":"0.8rem"}),
            ], md=5),
        ], className="mb-5"),
    ], fluid=True, style={"padding":"2rem 3rem","backgroundColor":"#060F1C"})


def register_callbacks(app):
    @app.callback(
        Output("resultado-prediccion","children"),
        Input("btn-predecir","n_clicks"),
        State("pred-edad","value"), State("pred-lectura","value"),
        State("pred-ultimo","value"), State("pred-score","value"),
        State("pred-deterioro","value"), State("pred-promedio","value"),
        State("pred-tecnologia","value"), State("pred-marca","value"),
        State("pred-diametro","value"), State("pred-metodo","value"),
        prevent_initial_call=True,
    )
    def predecir(n, edad, lectura, ultimo, score, deterioro, promedio,
                 tecnologia, diametro, metodo):
        if not MODEL_PATH.exists():
            return dbc.Alert("Modelo no disponible.",color="danger")
        try:
            with open(MODEL_PATH,"rb") as f: pipeline = pickle.load(f)
        except Exception as e:
            return dbc.Alert(f"Error cargando modelo: {e}",color="danger")

        row = pd.DataFrame([{
            "Edad del Medidor": edad or 0,
            "Lectura Acumulada": lectura or 0,
            "Ultimo Consumo Facturado": ultimo or 0,
            "Score de Priorizacion Asignado": score or 0,
            "Deterioro del Consumo": deterioro or 0,
            "Promedio de Consumo Real": promedio or 0,
            "Tecnologia": tecnologia or "Mecánico",
            "Diametro": diametro or '1/2"',
            "Ultimo Metodo Facturado": metodo or "Medido",
        }])

        try:
            pred = int(pipeline.predict(row)[0])
            prob = float(pipeline.predict_proba(row)[0][1])
        except Exception as e:
            return dbc.Alert(f"Error en predicción: {e}",color="danger")

        razones = []
        if edad and edad >= 10: razones.append(f"Edad crítica: {edad} años de servicio.")
        if deterioro and deterioro < -30: razones.append(f"Deterioro severo: {deterioro:.1f}%.")
        if metodo == "Estimado": razones.append("Último método Estimado (consumo no leído).")
        if promedio and promedio < 3: razones.append(f"Consumo promedio muy bajo: {promedio:.1f} m³.")
        if score and score > 60: razones.append(f"Score de priorización alto: {score:.0f}/100.")
        if not razones: razones.append("Perfil dentro de parámetros normales.")

        es1 = pred == 1
        color = "#EF4444" if es1 else "#10B981"
        titulo = "🔴 PRIORIDAD DE CAMBIO" if es1 else "🟢 ESTADO ÓPTIMO"
        msg = ("El modelo recomienda incluir este medidor en la próxima cuadrilla de reemplazo."
               if es1 else "El equipo opera dentro de parámetros normales.")

        return dbc.Card(dbc.CardBody([
            html.H4(titulo, style={"color":color,"fontWeight":"800","textAlign":"center",
                                   "fontFamily":"'Inter',sans-serif","marginBottom":"0.8rem"}),
            html.P(f"Probabilidad de cambio: {prob:.1%}",
                   style={"textAlign":"center","color":"#94a3b8","fontSize":"0.88rem",
                          "fontFamily":"'Inter',sans-serif","marginBottom":"0.4rem"}),
            dbc.Progress(value=prob*100,
                         color="danger" if prob>=0.7 else ("warning" if prob>=0.4 else "success"),
                         style={"height":"10px","borderRadius":"6px","marginBottom":"0.8rem"},
                         striped=True, animated=es1),
            html.P(msg, style={"color":"#cbd5e1","textAlign":"center","fontSize":"0.86rem",
                                "fontFamily":"'Inter',sans-serif","marginBottom":"0.8rem"}),
            html.Hr(style={"borderColor":"#1e3a5f"}),
            html.H6("Factores detectados:", style={"color":"#ffffff","fontWeight":"700",
                                                    "fontFamily":"'Inter',sans-serif","marginBottom":"0.4rem"}),
            html.Ul([html.Li(r, style={"color":"#94a3b8","fontSize":"0.83rem","fontFamily":"'Inter',sans-serif"})
                     for r in razones]),
            html.Hr(style={"borderColor":"#1e3a5f"}),
            dbc.Row([
                dbc.Col(html.Small(f"Edad: {edad}a | Deterioro: {deterioro}% | Consumo avg: {promedio} m³",
                                   style={"color":"#475569","fontSize":"0.76rem"})),
                dbc.Col(html.Small(f"Tecnología: {tecnologia} | Método: {metodo}",
                                   style={"color":"#475569","fontSize":"0.76rem"})),
            ]),
        ]), style={**_CARD,"borderLeft":f"5px solid {color}"})
