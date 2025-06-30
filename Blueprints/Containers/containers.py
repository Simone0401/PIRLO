# routes/containers.py
from flask import Blueprint, render_template, jsonify, abort, request, flash
import os, pathlib, subprocess 
import docker, docker.errors, datetime
from typing import Optional, List, Tuple
import logging
from utils.decorators import admin_only
from datetime import datetime
from datetime import timezone

DEBUG = False
# ───────────────────────────────────────────────────────────
containers_bp = Blueprint("containers", __name__, 
                          static_folder="static", static_url_path="static", 
                          template_folder="templates")

_client = docker.from_env()  # Inizializza il client Docker

# CAMBIA QUI: Definisci i percorsi dei servizi
PROJECTS = {
    "cannavaro": "/host/CANNAVARO-2.0",
    "totti":     "/host/TOTTI-2.0",
    "tulip":     "/host/TULIP",
    "pirlo":     "/host/PIRLO",
}

# ───────────────────────────────────────────────────────────
# Ritorna l'indirizzo IP dell'host
def get_host_ip() -> str:
   if os.getenv("HOST_IP"):
        return os.getenv("HOST_IP")
   return "localhost"

# ───────────────────────────────────────────────────────────
# Ritorna status del container
def container_status(name: str) -> str:
    """
    Ritorna 'running', 'exited', 'not-found', ecc.
    """
    try:
        return _client.containers.get(name).status      # 'running', 'exited'…
    except docker.errors.NotFound:
        return "not-found"

# ───────────────────────────────────────────────────────────
# Docker Compose Up
def compose_up(service: str, recreate: bool = False, env: list = os.environ.copy()) -> int:
    """
    Lancia `docker compose up -d` sul servizio richiesto.
    - recreate=False → up normale (ricrea solo se il file è cambiato)
    - recreate=True  → --force-recreate --build
    """
    project_dir = pathlib.Path(PROJECTS[service])
    compose_file = project_dir / "docker-compose.yml"
    if not compose_file.exists():
        raise FileNotFoundError(compose_file)
    
    cmd = ["docker", "compose", "-f", str(compose_file),
           "up", "-d"]
    if recreate:
        cmd += ["--build"]

    p = subprocess.run(cmd, check=True, cwd=project_dir, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if DEBUG:
        print(f"Comando eseguito: {' '.join(cmd)}")
        print(f"Output: {p.stdout.decode()}")
        print(f"Errori: {p.stderr.decode()}")
    return p.returncode

# ───────────────────────────────────────────────────────────
# Docker Compose Down
def compose_down(service: str, env: list = os.environ.copy()) -> int:
    """
    Lancia `docker compose down` sul servizio richiesto.
    """
    project_dir = pathlib.Path(PROJECTS[service])
    compose_file = project_dir / "docker-compose.yml"
    if not compose_file.exists():
        raise FileNotFoundError(compose_file)
    
    cmd = ["docker", "compose", "-f", str(compose_file),
           "down", "--remove-orphans"]

    p = subprocess.run(cmd, check=True, cwd=project_dir, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if DEBUG:
        print(f"Comando eseguito: {' '.join(cmd)}")
        print(f"Output: {p.stdout.decode()}")
        print(f"Errori: {p.stderr.decode()}")
    return p.returncode

# ───────────────────────────────────────────────────────────
# Ritorna i log del container come lista di tuple (timestamp, contenuto)
def get_logs_since(name: str, since: Optional[str] = None, tail: int = 200) -> List[Tuple[str, str]]:
    """
    Restituisce log come lista di tuple (timestamp, contenuto).
    - `since`: timestamp ISO8601 da cui iniziare (es: '2025-06-28T13:15:00')
    - `tail`: usato solo se `since` è None
    """
    c = _client.containers.get(name)

    kwargs = {
        "timestamps": True,
        "stdout": True,
        "stderr": True,
    }
    clean = None

    if since:
        clean = since.rstrip('Z')[:26]  # '2025-06-29T17:18:33.505436'
        dt = datetime.fromisoformat(clean).replace(tzinfo=timezone.utc)

        kwargs["since"] = dt.timestamp()

    else:
        kwargs["tail"] = tail

    raw = c.logs(**kwargs).decode(errors="ignore")
    result = []
    for line in raw.splitlines():
        if line.strip() == "":
            continue
        # Format: 2025-06-28T13:15:23.000000000Z Log content
        parts = line.split(" ", 1)
        if len(parts) == 2:
            ts, content = parts
            if not since or clean != ts.rstrip('Z')[:26]:
                result.append((ts, content))
    return result


# ───────────────────────────────────────────────────────────
# Docker Compose Build
def compose_build(service: str, env: list = os.environ.copy()) -> int:
    """
    Lancia `docker compose build` sul servizio richiesto.
    """
    project_dir = pathlib.Path(PROJECTS[service])
    compose_file = project_dir / "docker-compose.yml"
    if not compose_file.exists():
        raise FileNotFoundError(compose_file)

    cmd = ["docker", "compose", "-f", str(compose_file),
            "build"]

    p = subprocess.run(cmd, check=True, cwd=project_dir, env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if DEBUG:
        print(f"Comando eseguito: {' '.join(cmd)}")
        print(f"Output: {p.stdout.decode()}")
        print(f"Errori: {p.stderr.decode()}")
    return p.returncode

# ───────────────────────────────────────────────────────────
# 1.  Endpoint  /view
# ───────────────────────────────────────────────────────────
@containers_bp.route("/view", methods=["GET"])
def view_containers():
    host_ip = get_host_ip()

    containers = [
        {
            "id": "cannavaro",
            "name": "CANNAVARO",
            "logo": "images/cannavaro.png",
            "url": f"http://{host_ip}:7002",
        },
        {
            "id": "totti",
            "name": "TOTTI",
            "logo": "images/totti.png",
            "url": f"http://{host_ip}:5002",
        },
        {
            "id": "tulip",
            "name": "TULIP",
            "logo": "images/tulip.png",
            "url": f"http://{host_ip}:3000",
        },
        {
            "id": "pirlo",
            "name": "PIRLO",
            "logo": "images/pirlo.jpg",
            "url": f"http://{host_ip}:10000",
        },
    ]

    return render_template("view_containers.html", containers=containers)

# ───────────────────────────────────────────────────────────
# 2.  Endpoint  /containers/api/<cid>/status
# Ritorna lo stato del container come JSON
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/<cid>/status")
def api_container_status(cid):
    status = container_status(cid)
    return jsonify({"status": status})


# ───────────────────────────────────────────────────────────
# 3.  Endpoint  /containers/api/<cid>/start?recreate=X
# Avvia il container specificato
# - Se il container non esiste, ritorna 404
# - Se il container esiste, lo avvia e ritorna lo stato
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/<cid>/start", methods=["POST"])
@admin_only
def api_container_start(cid):
    if cid not in PROJECTS:
        abort(404, "Servizio sconosciuto")

    recreate = request.args.get("recreate") == "1"   # ?recreate=1 per build forzata
    try:
        result = compose_up(cid, recreate=recreate)
        status = container_status(cid)               # 'running' / 'exited'
        return jsonify(container=cid, result=result, status=status)
    except Exception as e:
        return jsonify(result=result, error=str(e)), 500
    
# ───────────────────────────────────────────────────────────
# 4.  Endpoint  /containers/api/<cid>/stop
# Stoppa il container specificato
# - Se il container non esiste, ritorna 404
# - Se il container esiste, lo termina e ritorna lo stato
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/<cid>/stop", methods=["POST"])
@admin_only
def api_container_stop(cid):
    if cid not in PROJECTS:
        abort(404, "Servizio sconosciuto")

    try:
        result = compose_down(cid)
        status = container_status(cid)               # 'running' / 'exited'
        return jsonify(container=cid, result=result, status=status)
    except Exception as e:
        return jsonify(result=result, error=str(e)), 500

# ───────────────────────────────────────────────────────────
# 5.  Endpoint  /containers/api/<cid>/build
# Builda il container specificato
# - Se il container non esiste, ritorna 404
# - Se il container esiste, lo builda e ritorna lo stato
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/<cid>/build", methods=["POST"])
@admin_only
def api_container_build(cid):
    if cid not in PROJECTS:
        abort(404, "Servizio sconosciuto")

    try:
        result = compose_build(cid)
        status = container_status(cid)               # 'running' / 'exited'
        return jsonify(container=cid, result=result, status=status)
    except Exception as e:
        return jsonify(result=result, error=str(e)), 500

# ───────────────────────────────────────────────────────────
# 6.  Endpoint  /containers/api/all-status
# Ritorna lo stato del container come JSON
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/all-status")
def api_all_status():
    return jsonify({
        "cannavaro": container_status("cannavaro"),
        "totti":     container_status("totti"),
        "tulip":     container_status("tulip"),
        "pirlo":     container_status("pirlo"),
    })

# ───────────────────────────────────────────────────────────
# 7.  Endpoint  /containers/api/<cid>/logs
# Ritorna i log del container come JSON
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/<cid>/logs")
def api_container_logs(cid):
    try:
        since = request.args.get("since")
        if cid == "tulip":
            cid = "tulip-assembler-1"
        logs = get_logs_since(cid, since)
        return jsonify(result=0, logs=logs)  # lista di [ [timestamp, riga], ... ]
    except docker.errors.NotFound:
        return jsonify(results=1, error="Container non trovato"), 404
    except Exception as e:
        return jsonify(result=1, error=str(e)), 500
    
# ───────────────────────────────────────────────────────────
# 8.  Endpoint  /containers/api/tulip/setup
# Esegue il setup di TULIP
# ───────────────────────────────────────────────────────────
@containers_bp.route("/api/tulip/setup", methods=["POST"])
@admin_only
def api_tulip_setup():
    try:
        project_dir = pathlib.Path(PROJECTS["tulip"])
        setup_script = project_dir / "setup.sh"
        if not setup_script.exists():
            return jsonify(result=1, error="Setup script non trovato"), 404
        
        cmd = ["bash", str(setup_script)]
        p = subprocess.run(cmd, check=True, cwd=project_dir,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if DEBUG:
            logging.info(f"Comando eseguito: {' '.join(cmd)}")
            logging.info(f"Output: {p.stdout.decode()}")
            logging.info(f"Errori: {p.stderr.decode()}")
        
        return jsonify(result=0, output=p.stdout.decode())
    except Exception as e:
        if DEBUG:
            logging.error(f"Comando eseguito: {' '.join(cmd)}")
            logging.error(f"Output: {p.stdout.decode()}")
            logging.error(f"Errori: {p.stderr.decode()}")
        return jsonify(result=1, error=str(e)), 500
    