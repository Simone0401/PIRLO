import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort, Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, DateTimeField
from wtforms.validators import DataRequired
from validators import *  # importa la funzione personalizzata
from wtforms.fields import DateTimeLocalField  # invece di html5
from dotenv import dotenv_values, set_key
from deployers.start_config import * 
from functools import wraps
import logging
from Blueprints.Containers.containers import containers_bp

# ----------------------
# Configurazione Flask
# ----------------------
app = Flask(__name__)

# Guarda Blueprints/Containers/containers.py per la definizione del Blueprint e delle route relative ai container
# Registra il Blueprint per le route dei container
app.register_blueprint(containers_bp, url_prefix='/containers')

# Prende la SECRET_KEY dall'env (docker-compose) oppure usa un valore di default (cambia in produzione!)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Percorso al file .global.env (nella cartella padre)
ENV_PATH = os.path.join('/', 'host', '.global.env')
logging.info(f"ENV_PATH: %s", ENV_PATH)

# all’inizio del tuo handler, oppure subito dopo aver definito ENV_PATH
if not os.path.exists(ENV_PATH):
    # crea un file vuoto, mantenendo i permessi della cartella
    open(ENV_PATH, 'a').close()

# ----------------------
# Definizione del form
# ----------------------
class ConfigForm(FlaskForm):
    vm_ip = StringField('VM Address', validators=[DataRequired(),IPOrHostname()])
    vm_password = PasswordField('VM Password', validators=[DataRequired()])
    vm_port = IntegerField('VM Port', validators=[DataRequired()])
    team = IntegerField('Team #', validators=[DataRequired()])
    number_of_teams = IntegerField('Numero totale squadre', validators=[DataRequired()])
    team_token = StringField('Team Token', validators=[DataRequired()])
    start_round = DateTimeLocalField(
        'Inizio Round',
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    traffic_dir_host = StringField('Cartella locale PCAP', validators=[DataRequired()])
    training = BooleanField('Modalità training')

# ----------------------
# Wrapper per limitare l'accesso a localhost
# ----------------------
def local_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if request.remote_addr not in ('127.0.0.1', '::1'):
            abort(403)
        return f(*args, **kwargs)
    return wrapped

# ----------------------
# Route principale
# ----------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConfigForm()
    if form.validate_on_submit():
        # Carica (o crea) .global.env
        # dotenv_values non crea file, ma set_key sì
        for key, val in {
            'VM_IP': form.vm_ip.data,
            'VM_PASSWORD': form.vm_password.data,
            'VM_PORT': str(form.vm_port.data),
            'TEAM': str(form.team.data),
            'NUMBER_OF_TEAMS': str(form.number_of_teams.data),
            'TEAM_TOKEN': form.team_token.data,
            'START_ROUND': form.start_round.data.isoformat(),
            'TRAFFIC_DIR_HOST': form.traffic_dir_host.data,
            'TRAINING': str(form.training.data).lower(),
        }.items():
            # set_key crea il file se non esiste e aggiunge/aggiorna le variabili
            set_key(ENV_PATH, key, val)

        flash('Configurazione salvata con successo in .global.env', 'success')
        
        # Avvia il deployer appropriato
        apply_config_route()

        return redirect(url_for('index'))

    return render_template('index.html', form=form)

# ----------------------
# Route start_config
# ----------------------
@app.route('/apply_config', methods=['GET'])
def apply_config_route():
    '''
    Route per applicare la configurazione tramite lo script apply_all_configs.sh
    '''
    returned_value = apply_config()
    if returned_value.returncode != 0:
        flash(f"Errore durante l'applicazione della configurazione: {returned_value.stdout}", 'danger')
    else:
        flash("Configurazione applicata correttamente!", 'success')

    return redirect(url_for('index'))

# ----------------------
# Avvio dell'app
# ----------------------
if __name__ == '__main__':
    # utile se fai `python app.py` direttamente
    app.run(host='0.0.0.0', port=5000)
