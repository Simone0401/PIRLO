# -*- coding: utf-8 -*-
import docker
from pathlib import Path
import os

PROJECT_DIR = '/host/CANNAVARO-2.0'

def start_cannavaro():
    """
    1) Avvia il docker-compose di CANNAVARO-2.0 usando il Docker SDK
    """
    # Avvia il compose upstream
    client = docker.from_env()   # userà /var/run/docker.sock
    # usa la CLI interna di Docker SDK per Compose
    # nota: richiede docker-compose-plugin installato sul host
    # in alternativa puoi usare client.containers.run() con immagine docker/compose
    os.system(f"docker-compose -f {PROJECT_DIR}/docker-compose.yml up -d")

def stop_cannavaro():
    """
    1) Termina il container di CANNAVARO-2.0 usando il Docker SDK
    """
    # Avvia il compose upstream
    client = docker.from_env()   # userà /var/run/docker.sock
    # usa la CLI interna di Docker SDK per Compose
    # nota: richiede docker-compose-plugin installato sul host
    # in alternativa puoi usare client.containers.run() con immagine docker/compose
    os.system(f"docker-compose -f {PROJECT_DIR}/docker-compose.yml down --remove-orphans")

def build_cannavaro():
    """
    1) Termina il container di CANNAVARO-2.0 usando il Docker SDK
    """
    # Avvia il compose upstream
    client = docker.from_env()   # userà /var/run/docker.sock
    # usa la CLI interna di Docker SDK per Compose
    # nota: richiede docker-compose-plugin installato sul host
    # in alternativa puoi usare client.containers.run() con immagine docker/compose
    os.system(f"docker-compose -f {PROJECT_DIR}/docker-compose.yml build")