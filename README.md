# Dashboard de Prediccion de Deterioro de Micromedidores
**Triple A — Barranquilla, Colombia**

Aplicacion analitica modular en Python/Dash que predice la prioridad de cambio
de micromedidores de agua, con el objetivo de reducir el Agua No Contabilizada
(ANC) y optimizar el despliegue de cuadrillas de mantenimiento.

---

## Estructura del proyecto

```
deterioro_medidores/
|-- app.py                      <- Punto de entrada principal
|-- requirements.txt
|-- Dockerfile
|-- docker-compose.yml
|-- assets/
|   `-- custom.css              <- Estilos globales del tema oscuro
|-- data/
|   `-- generate_data.py        <- Generador de dataset sintetico (si no tienes Historico.xlsx)
|-- model/
|   |-- train_model.py          <- Entrenamiento del Random Forest + serializacion
|   |-- model.pkl               <- Generado por train_model.py (no incluido en repo)
|   |-- metrics.json            <- Generado por train_model.py
|   `-- feature_names.json      <- Generado por train_model.py
`-- tabs/
    |-- contextoproblema.py     <- Pestana 1: Contexto operativo
    |-- eda.py                  <- Pestana 2: Analisis Exploratorio
    |-- metricasmodelo.py       <- Pestana 3: Metricas del modelo
    `-- prediccionmodelo.py     <- Pestana 4: Prediccion en tiempo real
```

---

## Dataset esperado

Archivo: `D:\garcieri\Documents\Curso Python\Historico.xlsx`

Columnas principales del dataset real:
| Columna | Tipo | Descripcion |
|---|---|---|
| Edad del Medidor | Numerica | Antiguedad en anos |
| Deterioro del Consumo | Numerica | Caida porcentual del consumo |
| Promedio de Consumo Real | Numerica | Media historica en m3 |
| Lectura Acumulada | Numerica | Odometro total del medidor |
| Ultimo Consumo Facturado | Numerica | Ultimo periodo en m3 |
| Score de Priorizacion Asignado | Numerica | Indice interno de riesgo |
| Tecnologia | Categorica | Mecanico / Estatico |
| Marca del Medidor | Categorica | ARAD, ELSTER, ITRON... |
| Diametro | Categorica | 1/2", 3/4", 1"... |
| Ultimo Metodo Facturado | Categorica | Medido, Estimado, Promedio... |
| Barrio | Categorica | Ubicacion del predio |
| **prioridad_cambio** | **Target** | **0=No cambiar / 1=Cambiar** |

Si el archivo no existe en la ruta configurada, el sistema busca
`data/Historico_sintetico.xlsx` generado por `data/generate_data.py`.

---

## Instalacion y ejecucion local

### Requisitos
- Python 3.10 o superior
- Windows, macOS o Linux

### Paso 1 — Crear entorno virtual

```bash
# En la carpeta del proyecto
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Mac/Linux
source venv/bin/activate
```

### Paso 2 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3 — (Opcional) Generar dataset sintetico

Solo si no tienes acceso a Historico.xlsx:

```bash
python data/generate_data.py
```

### Paso 4 — Entrenar el modelo

**Este paso es obligatorio antes de correr la app.**

```bash
python model/train_model.py
```

Genera tres archivos en `model/`:
- `model.pkl` — pipeline completo (preprocesador + Random Forest)
- `metrics.json` — accuracy, precision, recall, F1, AUC-ROC, curva ROC, matriz de confusion
- `feature_names.json` — opciones categoricas para el formulario interactivo

### Paso 5 — Ejecutar el dashboard

```bash
python app.py
```

Abrir en el navegador: **http://localhost:8050**

---

## Pestanas del dashboard

| # | Pestana | Contenido |
|---|---|---|
| 1 | **Contexto del Problema** | Impacto del ANC, evolucion del enfoque (reactivo -> predictivo), variables del dataset |
| 2 | **Analisis Exploratorio** | Top barrios criticos, boxplot consumo, histograma edad, apilado tecnologia, criticidad por marca |
| 3 | **Metricas del Modelo** | Tarjetas KPI, curva ROC, matriz de confusion, feature importances Top 15 |
| 4 | **Prediccion** | Formulario interactivo con sliders/dropdowns → resultado en tiempo real con colores de alerta |

---

## Stack tecnologico

| Capa | Tecnologia |
|---|---|
| Frontend | Dash 2.x + Dash Bootstrap Components (tema FLATLY) |
| Visualizacion | Plotly 6.x |
| Backend | Flask (via Dash) |
| Modelo | scikit-learn RandomForestClassifier |
| Datos | pandas + openpyxl |
| Produccion | Gunicorn + Docker |

---

## Despliegue con Docker

```bash
# Construir y levantar
docker-compose up --build

# Acceder en
http://localhost:8050
```

> **Nota:** El modelo debe entrenarse antes del build o dentro del Dockerfile.
> Descomenta la linea `RUN python model/train_model.py` en el Dockerfile si
> incluyes el dataset en la imagen.

---

## Equipo

Desarrollado por **Gio Garcia** — Triple A, Barranquilla, Colombia.
