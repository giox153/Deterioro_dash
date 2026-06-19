"""
model/train_model.py
Genera: model.pkl, metrics.json, feature_names.json, eda_summary.json
Ejecutar: python model/train_model.py
"""
import json, pickle, sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = Path(__file__).parent
HISTORICO_PATH = Path(r"D:\garcieri\Documents\Curso Python\Historico.xlsx")
SINTETICO_PATH = DATA_DIR / "Historico_sintetico.xlsx"

NUM_FEATURES = ["Edad del Medidor","Lectura Acumulada","Ultimo Consumo Facturado",
                "Score de Priorizacion Asignado","Deterioro del Consumo","Promedio de Consumo Real"]
CAT_FEATURES = ["Tecnologia","Marca del Medidor","Diametro","Ultimo Metodo Facturado"]
ALL_FEATURES = NUM_FEATURES + CAT_FEATURES
TARGET = "prioridad_cambio"

# Rangos fijos para el formulario (independiente del dataset, basado en dominio)
SLIDER_RANGES = {
    "Edad del Medidor":               {"min": 0,   "max": 35,   "mean": 7,    "step": 1},
    "Lectura Acumulada":              {"min": 0,   "max": 8000, "mean": 900,  "step": 50},
    "Ultimo Consumo Facturado":       {"min": 0,   "max": 60,   "mean": 13,   "step": 1},
    "Score de Priorizacion Asignado": {"min": 0,   "max": 100,  "mean": 35,   "step": 1},
    "Deterioro del Consumo":          {"min": -95, "max": 40,   "mean": -12,  "step": 1},
    "Promedio de Consumo Real":       {"min": 0,   "max": 80,   "mean": 15,   "step": 0.5},
}

def load_data():
    if HISTORICO_PATH.exists():
        print(f"Cargando: {HISTORICO_PATH}")
        return pd.read_excel(HISTORICO_PATH)
    elif SINTETICO_PATH.exists():
        print(f"Cargando sintetico: {SINTETICO_PATH}")
        return pd.read_excel(SINTETICO_PATH)
    else:
        sys.path.insert(0, str(DATA_DIR))
        from generate_data import generate
        return generate()

def preprocess(df):
    df = df.copy()
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df[TARGET] = df[TARGET].astype(int)
    for col in NUM_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in CAT_FEATURES:
        df[col] = df[col].astype(str).str.strip().fillna("DESCONOCIDO")
    return df

def build_eda_summary(df):
    """Pre-agrega todos los datos que necesitan las pestanas EDA."""
    print("Calculando resumen EDA...")
    summary = {}

    # 1. KPIs globales
    total = len(df)
    n1 = int(df[TARGET].sum())
    summary["kpis"] = {
        "total": total, "n_cambiar": n1, "n_no": total - n1,
        "pct_cambiar": round(n1/total*100, 2),
        "pct_no": round((total-n1)/total*100, 2),
    }

    # 2. Top 20 barrios criticos
    if "Barrio" in df.columns:
        df["prioridad_label"] = df[TARGET].map({0:"No Cambiar", 1:"Cambiar"})
        conteo = df["Barrio"].value_counts()
        validos = conteo[conteo >= 30].index
        dfsub = df[df["Barrio"].isin(validos)]
        cross = pd.crosstab(dfsub["Barrio"], dfsub[TARGET], normalize="index") * 100
        if 1 in cross.columns:
            cross = cross.reset_index()
            top = cross.nlargest(20, 1)[["Barrio", 1]].rename(columns={1:"pct"})
            top = top.sort_values("pct", ascending=True)
            summary["barrios"] = {"barrios": top["Barrio"].tolist(), "pct": top["pct"].round(1).tolist()}
        else:
            summary["barrios"] = {"barrios": [], "pct": []}

    # 3. Boxplot consumo por clase (5-number summary para no guardar raw data)
    for col in ["Promedio de Consumo Real", "Deterioro del Consumo"]:
        if col not in df.columns: continue
        key = col.replace(" ", "_").lower()
        result = {}
        for lbl, gdf in df.groupby(TARGET)[col]:
            s = gdf.dropna()
            p1, p99 = s.quantile(0.01), s.quantile(0.99)
            s = s.clip(p1, p99)
            result[int(lbl)] = {
                "min": round(float(s.min()),2), "q1": round(float(s.quantile(.25)),2),
                "median": round(float(s.median()),2), "q3": round(float(s.quantile(.75)),2),
                "max": round(float(s.max()),2), "mean": round(float(s.mean()),2),
                "name": "No Cambiar (0)" if lbl==0 else "Cambiar (1)"
            }
        summary[key] = result

    # 4. Histograma edad por clase (bins pre-calculados)
    if "Edad del Medidor" in df.columns:
        bins = list(range(0, 37, 1))
        hist_data = {}
        for lbl, gdf in df.groupby(TARGET)["Edad del Medidor"]:
            vals = gdf.dropna().clip(0, 35)
            counts, edges = np.histogram(vals, bins=bins, density=True)
            hist_data[int(lbl)] = {
                "x": [round((edges[i]+edges[i+1])/2, 1) for i in range(len(counts))],
                "y": counts.round(5).tolist(),
                "name": "No Cambiar (0)" if lbl==0 else "Cambiar (1)"
            }
        summary["edad_hist"] = hist_data

    # 5. Apilado tecnologia
    if "Tecnologia" in df.columns:
        cross_tec = pd.crosstab(df["Tecnologia"], df[TARGET], normalize="index") * 100
        cross_tec = cross_tec.reset_index()
        summary["tecnologia"] = {
            "tecnologias": cross_tec["Tecnologia"].tolist(),
            "pct_0": cross_tec.get(0, pd.Series([0]*len(cross_tec))).round(1).tolist(),
            "pct_1": cross_tec.get(1, pd.Series([0]*len(cross_tec))).round(1).tolist(),
        }

    # 6. Criticidad por marca
    if "Marca del Medidor" in df.columns:
        cross_m = pd.crosstab(df["Marca del Medidor"], df[TARGET], normalize="index") * 100
        if 1 in cross_m.columns:
            cross_m = cross_m.reset_index().rename(columns={1:"pct"})
            cross_m = cross_m.sort_values("pct", ascending=True)
            summary["marcas"] = {
                "marcas": cross_m["Marca del Medidor"].tolist(),
                "pct": cross_m["pct"].round(1).tolist()
            }

    return summary

def train_and_evaluate():
    df_raw = load_data()
    df = preprocess(df_raw)
    print(f"Registros: {len(df):,} | Clase 1: {df[TARGET].mean()*100:.1f}%")

    X, y = df[ALL_FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUM_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT_FEATURES),
    ], remainder="drop")

    clf = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_leaf=10,
                                  class_weight="balanced", random_state=42, n_jobs=-1)
    pipeline = Pipeline([("preprocessor", preprocessor), ("classifier", clf)])

    print("Entrenando...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()

    feat_names = pipeline.named_steps["preprocessor"].get_feature_names_out().tolist()
    importances = pipeline.named_steps["classifier"].feature_importances_.tolist()

    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score":  round(f1_score(y_test, y_pred, zero_division=0), 4),
        "auc_roc":   round(roc_auc_score(y_test, y_prob), 4),
        "confusion_matrix": cm,
        "roc_fpr": [round(x,4) for x in fpr.tolist()[::5]],  # downsample
        "roc_tpr": [round(x,4) for x in tpr.tolist()[::5]],
        "feature_importances": {n: round(v,6) for n,v in zip(feat_names, importances)},
        "n_test": int(len(y_test)),
        "class_distribution": {
            "clase_0_pct": round((df[TARGET]==0).mean()*100, 2),
            "clase_1_pct": round((df[TARGET]==1).mean()*100, 2),
        },
    }

    cat_options = {col: sorted(df[col].unique().tolist()) for col in CAT_FEATURES}
    feature_meta = {
        "num_features": NUM_FEATURES, "cat_features": CAT_FEATURES,
        "cat_options": cat_options,
        "num_ranges": SLIDER_RANGES,  # Siempre rangos fijos del dominio
    }

    eda_summary = build_eda_summary(df)

    MODEL_DIR.mkdir(exist_ok=True)
    with open(MODEL_DIR / "model.pkl", "wb") as f: pickle.dump(pipeline, f)
    with open(MODEL_DIR / "metrics.json", "w", encoding="utf-8") as f: json.dump(metrics, f, indent=2)
    with open(MODEL_DIR / "feature_names.json", "w", encoding="utf-8") as f: json.dump(feature_meta, f, ensure_ascii=False, indent=2)
    with open(MODEL_DIR / "eda_summary.json", "w", encoding="utf-8") as f: json.dump(eda_summary, f, ensure_ascii=False, indent=2)

    print(f"\nMetricas: Acc={metrics['accuracy']} | F1={metrics['f1_score']} | AUC={metrics['auc_roc']}")
    print("Archivos guardados: model.pkl, metrics.json, feature_names.json, eda_summary.json")

if __name__ == "__main__":
    train_and_evaluate()
