"""tabs/metricasmodelo.py - Lee metrics.json, sin pandas."""
import json
from pathlib import Path
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc

MODEL_DIR   = Path(__file__).parent.parent / "model"
METRICS_PATH = MODEL_DIR / "metrics.json"

_TITLE = {"color":"#ffffff","fontWeight":"800","fontSize":"1.75rem",
          "borderLeft":"6px solid #3B82F6","paddingLeft":"16px",
          "fontFamily":"'Inter','Segoe UI',sans-serif"}
_SUB   = {"color":"#94a3b8","fontSize":"0.88rem","fontFamily":"'Inter','Segoe UI',sans-serif","marginBottom":"1rem"}
_SEC   = {"color":"#ffffff","fontWeight":"700","fontSize":"1rem","fontFamily":"'Inter','Segoe UI',sans-serif","marginBottom":"0.3rem"}
_CARD  = {"backgroundColor":"#0D1E35","border":"1px solid #1e3a5f","borderRadius":"14px"}

# Layout base SIN xaxis/yaxis para evitar duplicados
_PL = dict(paper_bgcolor="#0D1E35", plot_bgcolor="#0D1E35",
           font=dict(color="#cbd5e1", family="Inter,sans-serif", size=11),
           margin=dict(t=45,b=35,l=55,r=20),
           title_font=dict(color="#ffffff",size=12),
           legend=dict(bgcolor="#0D1E35",bordercolor="#1e3a5f",borderwidth=1))
_AX = dict(gridcolor="#1e3a5f", color="#94a3b8")

def _load():
    if not METRICS_PATH.exists(): return {}
    with open(METRICS_PATH,"r",encoding="utf-8") as f: return json.load(f)

def _kpi(label, valor, color, tip=""):
    v = f"{valor:.4f}" if isinstance(valor, float) else str(valor)
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.H3(v, style={"color":color,"fontWeight":"800","textAlign":"center",
                          "fontSize":"1.8rem","fontFamily":"'Inter',sans-serif","marginBottom":"0.2rem"}),
        html.P(label, style={"textAlign":"center","color":"#94a3b8","fontSize":"0.8rem","marginBottom":"0"}),
        html.P(tip,   style={"textAlign":"center","color":"#64748b","fontSize":"0.73rem","marginBottom":"0"}),
    ]),style=_CARD), md=True, className="mb-3")

def _fig_roc(m):
    fpr = m.get("roc_fpr",[0,1]); tpr = m.get("roc_tpr",[0,1]); auc = m.get("auc_roc",0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr,y=tpr,mode="lines",name=f"AUC={auc:.4f}",
                             line=dict(color="#3B82F6",width=2.5),fill="tozeroy",fillcolor="rgba(59,130,246,0.1)"))
    fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",name="Azar",
                             line=dict(color="#64748b",width=1.5,dash="dash")))
    fig.update_layout(**_PL, title=f"Curva ROC — AUC={auc:.4f}", height=400,
                      xaxis=dict(**_AX, title="FPR", range=[0,1]),
                      yaxis=dict(**_AX, title="TPR", range=[0,1.02]))
    return fig

def _fig_cm(m):
    cm = np.array(m.get("confusion_matrix",[[0,0],[0,0]]))
    rs = cm.sum(axis=1, keepdims=True)
    cn = np.where(rs>0, cm.astype(float)/rs, 0.0)
    labs = ["No Cambiar (0)","Cambiar (1)"]
    txt  = [[f"{cm[i][j]:,}<br>({cn[i][j]:.1%})" for j in range(2)] for i in range(2)]
    fig  = go.Figure(go.Heatmap(z=cn, x=labs, y=labs,
                                colorscale=[[0,"#0D1E35"],[0.5,"#1e3a5f"],[1,"#3B82F6"]],
                                showscale=True, text=txt, texttemplate="%{text}",
                                textfont=dict(size=13,color="#ffffff")))
    fig.update_layout(**_PL, title="Matriz de Confusión", height=370,
                      xaxis=dict(**_AX, title="Predicción", side="bottom"),
                      yaxis=dict(**_AX, title="Real", autorange="reversed"))
    return fig

def _fig_imp(m):
    imp = m.get("feature_importances",{})
    if not imp: return go.Figure()
    items = sorted(imp.items(), key=lambda x: x[1], reverse=True)[:15]
    names = [n.replace("num__","").replace("cat__","").replace("_"," ") for n,_ in items]
    vals  = [v for _,v in items]
    names.reverse(); vals.reverse()
    fig = go.Figure(go.Bar(x=vals, y=names, orientation="h",
                           marker=dict(color=vals, colorscale=[[0,"#1e3a5f"],[1,"#3B82F6"]]),
                           text=[f"{v:.4f}" for v in vals], textposition="outside",
                           textfont=dict(color="#cbd5e1",size=10)))
    fig.update_layout(**_PL, title="Top 15 Variables — Importancia (Gini)", height=460,
                      xaxis=dict(**_AX, title="Importancia"),
                      yaxis=dict(**_AX, tickfont=dict(size=9)), showlegend=False)
    return fig

def layout():
    m = _load()
    if not m:
        return dbc.Container([
            dbc.Row([dbc.Col([html.H1("Métricas del Modelo",style=_TITLE),
                              html.Hr(style={"borderColor":"#1e3a5f"})])],className="mt-4"),
            dbc.Alert([html.Strong("Modelo no encontrado. "),
                       "Ejecuta: ", html.Code("python model/train_model.py")],color="warning"),
        ], fluid=True, style={"padding":"2rem 3rem","backgroundColor":"#060F1C"})

    dist = m.get("class_distribution",{})
    return dbc.Container([
        dbc.Row([dbc.Col([html.H1("Métricas del Modelo",style=_TITLE),
                          html.P("Random Forest — evaluado en 20% hold-out estratificado.",style=_SUB),
                          html.Hr(style={"borderColor":"#1e3a5f"})])],className="mt-4"),

        dbc.Row([
            _kpi("Accuracy",  m.get("accuracy",0),  "#3B82F6","Exactitud global"),
            _kpi("Precision", m.get("precision",0), "#10B981","TP/(TP+FP)"),
            _kpi("Recall",    m.get("recall",0),    "#E07B2A","TP/(TP+FN)"),
            _kpi("F1-Score",  m.get("f1_score",0),  "#A855F7","Media armónica"),
            _kpi("AUC-ROC",   m.get("auc_roc",0),   "#EF4444","Discriminación"),
        ]),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([dbc.Col([dbc.Card(dbc.CardBody([
            html.P(f"Distribución: Clase 0 = {dist.get('clase_0_pct','?')}% | "
                   f"Clase 1 = {dist.get('clase_1_pct','?')}%. "
                   "El modelo usa class_weight='balanced'. Recall y F1 son las métricas relevantes en desbalance.",
                   style={"color":"#cbd5e1","fontSize":"0.88rem","lineHeight":"1.7",
                          "fontFamily":"'Inter',sans-serif","marginBottom":"0"}),
        ]),style={**_CARD,"borderLeft":"4px solid #E07B2A"})])],className="mb-4"),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([
            dbc.Col([html.H5("Curva ROC",style=_SEC),
                     dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_roc(m),config={"displayModeBar":False})]),style=_CARD)],md=6),
            dbc.Col([html.H5("Matriz de Confusión",style=_SEC),
                     dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_cm(m),config={"displayModeBar":False})]),style=_CARD)],md=6),
        ],className="mb-4"),

        html.Hr(style={"borderColor":"#1e3a5f"}),

        dbc.Row([dbc.Col([html.H5("Importancia de Variables",style=_SEC),
                          dbc.Card(dbc.CardBody([dcc.Graph(figure=_fig_imp(m),config={"displayModeBar":False})]),style=_CARD)])
                 ],className="mb-5"),

    ], fluid=True, style={"padding":"2rem 3rem","backgroundColor":"#060F1C"})
