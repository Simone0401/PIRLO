# 1) Base image Python slimmata
FROM python:3.9-slim

# 2) Imposto la working directory
WORKDIR /app

# 3) Copio e installo solo le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copio il resto del codice dell’app
COPY . .

# 5) Espongo la porta su cui gira Flask
EXPOSE 5000

# 6) Variabili d’ambiente per Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 7) Comando di avvio
CMD ["flask", "run"]
