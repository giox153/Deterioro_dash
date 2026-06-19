"""
tabs/eda.py - Lee eda_summary.json (pre-calculado por train_model.py). Carga instantanea.
"""
import json
from pathlib import Path
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc

MODEL_DIR = Path(__file__).parent.parent / "model"
EDA_PATH  = MODEL_DIR / "eda_summary.json"

_TITLE = {"color":"#ffffff","fontWeight":"800","fontSize":"1.75rem",
          "borderLeft":"6px solid #E07B2A","paddingLeft":"16px",
          "fontFamily":"'Inter','Segoe UI',sans-serif"}
_SUB   = {"color":"#94a3b8","fontSize":"0.85rem","fontFamily":"'Inter','Segoe UI',sans-serif","marginBottom":"0.8rem"}
_SEC   = {"color":"#ffffff","fontWeight":"700","fontSize":"1rem","fontFamily":"'Inter','Segoe UI',sans-serif","marginBottom":"0.3rem"}
_CARD  = {"backgroundColor":"#0D1E35","border":"1px solid #1e3a5f","borderRadius":"14px"}
_PL    = dict(paper_bgcolor="#0D1E35",plot_bgcolor="#0D1E35",
              font=dict(color="#cbd5e1",family="Inter,sans-serif",size=11),
              margin=dict(t=45,b=35,l=55,r=20),
              title_font=dict(color="#ffffff",size=12),
              legend=dict(bgcolor="#0D1E35",bordercolor="#1e3a5f",borderwidth=1))
_AX    = dict(gridcolor="#1e3a5f",color="#94a3b8")

def _load():
    if not EDA_PATH.exists(): return None
    with open(EDA_PATH,"r",encoding="utf-8") as f: return json.load(f)

def _fig_barrios(s):
    d = s.get("barrios",{})
    if not d.get("barrios"): return go.Figure()
    fig = go.Figure(go.Bar(
        x=d["pct"], y=d["barrios"], orientation="h",
        marker=dict(color=d["pct"], colorscale=[[0,"#E07B2A"],[1,"#7F1D1D"]], showscale=False),
        text=[f"{v:.1f}%" for v in d["pct"]], textposition="outside",
        textfont=dict(color="#cbd5e1",size=10),
        hovertemplate="<b>%{y}</b><br>Criticidad: %{x:.1f}%<extra></extra>"))
    fig.update_layout(**_PL, title="Top 20 Barrios — % Medidores a Cambiar",
                      xaxis=dict(**_AX,ticksuffix="%",title="% Prioridad"),
                      yaxis=dict(**_AX,tickfont=dict(size=9)), height=500, showlegend=False)
    return fig

def _fig_box(s, key, title, ytitle):
    d = s.get(key, {})
    if not d: return go.Figure()
    colores = {0:"#3B82F6", 1:"#EF4444"}
    fig = go.Figure()
    for lbl_str, info in d.items():
        lbl = int(lbl_str)
        fig.add_trace(go.Box(
            q1=[info["q1"]], median=[info["median"]], q3=[info["q3"]],
            lowerfence=[info["min"]], upperfence=[info["max"]], mean=[info["mean"]],
            name=info["name"], marker_color=colores.get(lbl,"#94a3b8"),
            line=dict(color=colores.get(lbl,"#94a3b8"),width=2),
            boxmean=True))
    fig.update_layout(**_PL, title=title, barmode="group",
                      yaxis=dict(**_AX,title=ytitle), height=380)
    return fig

def _fig_edad(s):
    d = s.get("edad_hist",{})
    if not d: return go.Figure()
    colores = {0:"#3B82F6", 1:"#EF4444"}
    fig = go.Figure()
    for lbl_str, info in d.items():
        lbl = int(lbl_str)
        fig.add_trace(go.Bar(
            x=info["x"], y=info["y"], name=info["name"],
            marker=dict(color=colores.get(lbl,"#94a3b8"), opacity=0.65),
            hovertemplate=f"<b>{info['name']}</b><br>Edad: %{{x}} años<br>Densidad: %{{y:.4f}}<extra></extra>"))
    fig.update_layout(**_PL, title="Distribución Edad del Medidor por Estado de Reemplazo",
                      barmode="overlay",
                      xaxis=dict(**_AX,title="Edad (Años)"),
                      yaxis=dict(**_AX,title="Densidad"), height=380)
    return fig

def _fig_tecnologia(s):
    d = s.get("tecnologia",{})
    if not d: return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="No Cambiar (0)", x=d["tecnologias"], y=d["pct_0"],
                         marker_color="#3B82F6", opacity=0.85,
                         text=[f"{v:.1f}%" for v in d["pct_0"]], textposition="inside",
                         textfont=dict(color="#fff",size=11)))
    fig.add_trace(go.Bar(name="Cambiar (1)", x=d["tecnologias"], y=d["pct_1"],
                         marker_color="#EF4444", opacity=0.85,
                         text=[f"{v:.1f}%" for v in d["pct_1"]], textposition="inside",
                         textfont=dict(color="#fff",size=11)))
    fig.update_layout(**_PL, title="Tasa de Reemplazo por Tecnología (Apilado 100%)",
                      barmode="stack",
                      yaxis=dict(**_AX,title="%",ticksuffix="%"), height=360)
    return fig

def _fig_marcas(s):
    d = s.get("marcas",{})
    if not d: return go.Figure()
    fig = go.Figure(go.Bar(
        x=d["pct"], y=d["marcas"], orientation="h",
        marker=dict(color="#E07B2A", opacity=0.85),
        text=[f"{v:.1f}%" for v in d["pct"]], textposition="outside",
        textfont=dict(color="#cbd5e1",size=10)))
    fig.update_layout(**_PL, title="% Prioridad de Cambio por Marca del Medidor",
                      xaxis=dict(**_AX,ticksuffix="%"),
                      yaxis=dict(**_AX), height=340, showlegend=False)
    return fig

def layout():
    s = _load()
    if s is None:
        return dbc.Container([
            dbc.Row([dbc.Col([html.H1("Análisis Exploratorio",style=_TITLE),
                              html.Hr(style={"borderColor":"#1e3a5f"})])],className="mt-4"),
            dbc.Alert([html.Strong("EDA no disponible. "),
                       "Ejecuta: ", html.Code("python model/train_model.py")],
                      color="warning",className="mb-4"),
        ], fluid=True, style={"padding":"2rem 3rem","backgroundColor":"#060F1C"})

    kpis_d = s.get("kpis",{})
    kpis = [
        {"v": f"{kpis_d.get('total',0):,}",         "l":"Registros totales",     "c":"#3B82F6"},
        {"v": f"{kpis_d.get('n_cambiar',0):,}",      "l":"Prioridad Cambio (1)", "c":"#EF4444"},
        {"v": f"{kpis_d.get('n_no',0):,}",           "l":"Estado Normal (0)",    "c":"#10B981"},
        {"v": f"{kpis_d.get('pct_cambiar',0):.1f}%","l":"Tasa de Criticidad",   "c":"#E07B2A"},
    ]

    return dbc.Container([
        dbc.Row([dbc.Col([html.H1("Análisis Exploratorio de Datos (EDA)",style=_TITLE),
                          html.P("Deterioro de medidores",style=_SUB),
                          html.Hr(style={"borderColor":"#1e3a5f"})])],className="mt-4"),

        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H3(k["v"],style={"color":k["c"],"fontWeight":"800","textAlign":"center","fontFamily":"'Inter',sans-serif"}),
                html.P(k["l"],style={"textAlign":"center","color":"#94a3b8","fontSize":"0.8rem","marginBottom":"0"}),
            ]),style=_CARD), md=3, className="mb-3")
            for k in kpis
        ]),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([dbc.Col([
            html.H5("🏙️ Top Barrios — Índice de Criticidad",style=_SEC),
            html.P("Barrios con mayor % de medidores en prioridad de cambio (mín. 30 equipos).",style=_SUB),
            dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_barrios(s),config={"displayModeBar":False})]),style=_CARD),
        ])], className="mb-4"),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([
            dbc.Col([
                html.H5("📦 Consumo Promedio vs Prioridad",style=_SEC),
                html.P("Medidores críticos registran menor consumo (submedición).",style=_SUB),
                dbc.Card(dbc.CardBody([dcc.Graph(
                    figure=_fig_box(s,"promedio_de_consumo_real","Consumo Promedio Real (m³) por Estado","m³"),
                    config={"displayModeBar":False})]),style=_CARD),
            ], md=6),
            dbc.Col([
                html.H5("📉 Deterioro del Consumo",style=_SEC),
                html.P("Caída porcentual del consumo — huella matemática de la submedición.",style=_SUB),
                dbc.Card(dbc.CardBody([dcc.Graph(
                    figure=_fig_box(s,"deterioro_del_consumo","Deterioro del Consumo (%) por Estado","%"),
                    config={"displayModeBar":False})]),style=_CARD),
            ], md=6),
        ], className="mb-4"),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([dbc.Col([
            html.H5("⏳ Edad del Medidor por Estado de Reemplazo",style=_SEC),
            html.P("Solapamiento en edades intermedias justifica usar ML en lugar de reglas simples de antigüedad.",style=_SUB),
            dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_edad(s),config={"displayModeBar":False})]),style=_CARD),
        ])], className="mb-4"),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([
            dbc.Col([
                html.H5("⚙️ Reemplazo por Tecnología (100%)",style=_SEC),
                html.P("Proporción de prioridad por tipo de medidor.",style=_SUB),
                dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_tecnologia(s),config={"displayModeBar":False})]),style=_CARD),
            ], md=6),
            dbc.Col([
                html.H5("🏷️ Criticidad por Marca",style=_SEC),
                html.P("Marcas con mayor propensión a fallo en Barranquilla.",style=_SUB),
                dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_marcas(s),config={"displayModeBar":False})]),style=_CARD),
            ], md=6),
        ], className="mb-5"),

    ], fluid=True, style={"padding":"2rem 3rem","backgroundColor":"#060F1C"})
