"""
data/generate_data.py
=====================
Genera un dataset sintético que replica la estructura de Historico.xlsx.
Úsalo SOLO si el Excel original no está disponible.
Columnas reales del archivo fuente:
  Cuenta, Nombre del Cliente, Municipio, Direccion, Barrio,
  Edad del Medidor, Marca del Medidor, Tecnologia, Diametro,
  Lectura Acumulada, Ultimo Metodo Facturado, Ultimo Consumo Facturado,
  Observacion del Lector, Zona de Presion, Sector, Circuito,
  Latitud, Longitud, Score de Priorizacion Asignado,
  Deterioro del Consumo, Fecha, Promedio de Consumo Real,
  prioridad_cambio (target: 0=No cambiar, 1=Cambiar)
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N = 12_000  # registros sintéticos

BARRIOS = [
    "El Prado", "Boston", "Manga", "Rebolo", "Las Nieves",
    "Riomar", "Ciudad Jardín", "Las Palmas", "Modelo", "La Paz",
    "Bellavista", "Chiquinquirá", "Los Olivos", "Villate", "La Gloria",
    "Campo Alegre", "San Roque", "Paraíso", "El Porvenir", "Siape",
]

MARCAS = ["ARAD", "ELSTER", "ITRON", "SENSUS", "ZENNER", "AQUA"]
TECNOLOGIAS = ["Mecánico", "Estático"]
DIAMETROS = ['1/2"', '3/4"', '1"', '1 1/2"', '2"']
METODOS = ["Medido", "Estimado", "Promedio", "Aforo", "Lectura Real"]
OBSERVACIONES = [
    "SIN NOVEDAD", "MEDIDOR FRENADO", "MEDIDOR ROTO",
    "ACCESO NEGADO", "MEDIDOR ENTERRADO", None, None,
]
ZONAS = ["ZP-1", "ZP-2", "ZP-3", "ZP-4", "ZP-5"]
SECTORES = [f"SEC-{i:02d}" for i in range(1, 9)]
CIRCUITOS = [f"CIR-{i:03d}" for i in range(1, 25)]


def generate():
    # ── Variables categóricas ────────────────────────────────────────────────
    barrio = RNG.choice(BARRIOS, N)
    marca = RNG.choice(MARCAS, N, p=[0.30, 0.20, 0.18, 0.15, 0.10, 0.07])
    tecnologia = RNG.choice(TECNOLOGIAS, N, p=[0.82, 0.18])
    diametro = RNG.choice(DIAMETROS, N, p=[0.65, 0.20, 0.10, 0.03, 0.02])
    metodo = RNG.choice(METODOS, N, p=[0.55, 0.25, 0.12, 0.05, 0.03])
    observacion = RNG.choice(OBSERVACIONES, N)
    zona = RNG.choice(ZONAS, N)
    sector = RNG.choice(SECTORES, N)
    circuito = RNG.choice(CIRCUITOS, N)

    # ── Variables numéricas ──────────────────────────────────────────────────
    edad = np.clip(RNG.exponential(scale=7, size=N), 0, 35).astype(int)

    # Consumo promedio: medidores viejos tienden a subregistrar (menor promedio)
    promedio_consumo = np.clip(
        18 - 0.35 * edad + RNG.normal(0, 6, N), 0.5, 120
    )

    # Último consumo: puede ser 0 si el medidor está frenado
    frenados = RNG.random(N) < 0.12
    ultimo_consumo = np.where(
        frenados,
        0,
        np.clip(promedio_consumo * RNG.uniform(0.4, 1.6, N), 0, 150),
    ).astype(int)

    # Deterioro del consumo (porcentaje de caída, negativo = subreporte)
    deterioro = np.clip(
        -(edad * 1.8 + RNG.normal(0, 15, N)), -95, 40
    )

    lectura_acum = np.clip(
        edad * promedio_consumo * 10 + RNG.normal(0, 200, N), 0, 30_000
    )

    score = np.clip(
        (edad * 0.4 + abs(deterioro) * 0.3 + (promedio_consumo < 5) * 30
         + RNG.normal(0, 5, N)),
        0, 100,
    )

    # Coordenadas de Barranquilla (aprox.)
    lat = RNG.uniform(10.95, 11.05, N)
    lon = RNG.uniform(-74.85, -74.73, N)

    fechas = pd.date_range("2024-01-01", periods=12, freq="MS")
    fecha = RNG.choice(fechas, N)

    # ── Variable respuesta: prioridad_cambio ─────────────────────────────────
    # Probabilidad de cambio guiada por lógica real del negocio
    prob_cambio = (
        0.03 * edad
        + 0.015 * abs(deterioro)
        + 0.25 * (metodo == "Estimado")
        + 0.40 * frenados.astype(float)
        + 0.10 * (tecnologia == "Mecánico").astype(float)
        + RNG.uniform(0, 0.15, N)
    )
    prob_cambio = np.clip(prob_cambio / prob_cambio.max(), 0.02, 0.97)
    prioridad_cambio = (RNG.random(N) < prob_cambio).astype(int)

    # ── Ensamblaje ───────────────────────────────────────────────────────────
    df = pd.DataFrame({
        "Cuenta": RNG.integers(100_000, 999_999, N),
        "Nombre del Cliente": [f"CLIENTE_{i:06d}" for i in range(N)],
        "Municipio": "BARRANQUILLA",
        "Direccion": [f"CL {RNG.integers(1, 120)} # {RNG.integers(1, 80)}-{RNG.integers(1, 99)}" for _ in range(N)],
        "Barrio": barrio,
        "Edad del Medidor": edad,
        "Marca del Medidor": marca,
        "Tecnologia": tecnologia,
        "Diametro": diametro,
        "Lectura Acumulada": lectura_acum.round(1),
        "Ultimo Metodo Facturado": metodo,
        "Ultimo Consumo Facturado": ultimo_consumo,
        "Observacion del Lector": observacion,
        "Zona de Presion": zona,
        "Sector": sector,
        "Circuito": circuito,
        "Latitud": lat.round(6),
        "Longitud": lon.round(6),
        "Score de Priorizacion Asignado": score.round(2),
        "Deterioro del Consumo": deterioro.round(2),
        "Fecha": fecha,
        "Promedio de Consumo Real": promedio_consumo.round(2),
        "prioridad_cambio": prioridad_cambio,
    })

    out_path = Path(__file__).parent / "Historico_sintetico.xlsx"
    df.to_excel(out_path, index=False)
    print(f"✅ Dataset sintético generado: {out_path}  ({N} registros)")
    return df


if __name__ == "__main__":
    generate()
