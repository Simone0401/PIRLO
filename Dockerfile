# 1) Base image Python slimmata
FROM python:3.9-slim

# 2) Imposto la working directory
WORKDIR /app

# 2.1) Installo le dipendenze di sistema necessarie
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       jq \
       docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create the directory where the Docker Compose plugin will be installed and install Docker Compose V2.
RUN mkdir -p /usr/local/lib/docker/cli-plugins/ \
    && curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m) \
         -o /usr/local/lib/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

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
ENV FLASK_ENV=development

# 7) Comando di avvio
CMD ["flask", "run", "--host=0.0.0", "--reload"]
