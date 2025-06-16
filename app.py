import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, IPAddress
from dotenv import dotenv_values, set_key

# ----------------------
# Configurazione Flask
# ----------------------
app = Flask(__name__)
# Prende la SECRET_KEY dall'env (docker-compose) oppure usa un valore di default (cambia in produzione!)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Percorso al file .global.env (nella cartella padre)
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', '.global.env'))

# ----------------------
# Definizione del form
# ----------------------
class ConfigForm(FlaskForm):
    vm_ip = StringField('VM IP', validators=[DataRequired(), IPAddress()])
    vm_password = PasswordField('VM Password', validators=[DataRequired()])
    vm_port = IntegerField('VM Port', validators=[DataRequired()])
    team = IntegerField('Team #', validators=[DataRequired()])
    number_of_teams = IntegerField('Numero totale squadre', validators=[DataRequired()])
    team_token = StringField('Team Token', validators=[DataRequired()])
    start_round = DateTimeField(
        'Inizio Round (YYYY-MM-DDThh:mm±ZZ:ZZ)',
        format="%Y-%m-%dT%H:%M%z",
        validators=[DataRequired()]
    )
    traffic_dir_host = StringField('Cartella locale PCAP', validators=[DataRequired()])
    training = BooleanField('Modalità training')

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
        return redirect(url_for('index'))

    return render_template('index.html', form=form)

# ----------------------
# Avvio dell'app
# ----------------------
if __name__ == '__main__':
    # utile se fai `python app.py` direttamente
    app.run(host='0.0.0.0', port=5000)
