FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para openpyxl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrenar el modelo al buildear (requiere Historico_sintetico.xlsx en /app/data)
# RUN python model/train_model.py

EXPOSE 8050

CMD ["gunicorn", "app:server", \
     "--bind", "0.0.0.0:8050", \
     "--workers", "2", \
     "--timeout", "120"]
