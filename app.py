import shutil

from flask_mail import Mail, Message
import os
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, flash, url_for, \
    session, jsonify, logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
import requests

# Configurazione del logger


app = Flask(__name__)
app.secret_key = 'tuo_segreto'  # Necessario per visualizzare messaggi di conferma
app.config['PRODUCTION'] = False  # Imposta a True in produzione
app.config['RECAPTCHA_SECRET_KEY'] = '6LfRNVMgAAAAAN0pabmCJdANjHphZ2pX-Pzx-1yg'

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('access.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app.logger.addHandler(handler)

@app.after_request
def log_request(response):
    app.logger.info(f"IP: {request.remote_addr} - Request: {request.method} {request.scheme}://{request.host}{request.path} - Response: {response.status_code}")
    return response

app.after_request(log_request)

# Configurazione email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gianlucaproto@gmail.com'
app.config['MAIL_PASSWORD'] = 'ziojaemccrrjydyp'

mail = Mail(app)  # Corretta inizializzazione

# Dummy dati di login per l'amministratore
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'


# Configurazione del percorso per il caricamento delle immagini
gallery_upload_folder = os.path.join('static', 'img', 'gallery/altro')
if not os.path.exists(gallery_upload_folder):
    os.makedirs(gallery_upload_folder)

# Definizione del form di login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    image = FileField('Carica Immagine', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo immagini!')])
    submit = SubmitField('Carica')


# Definisci una funzione decorator per verificare se l'utente è loggato
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/commissions')
def commissions():
    return render_template('commissions.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        recaptcha_response = request.form.get('recaptcha_response')
        if not recaptcha_response:
            flash('Errore di verifica CAPTCHA: nessuna risposta fornita.', 'error')
            return redirect('/contact')

        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': app.config['RECAPTCHA_SECRET_KEY'],
                'response': recaptcha_response
            }
        )
        result = response.json()
        if not result.get('success', False) or result.get('score', 0) < 0.5:
            flash('Errore di verifica CAPTCHA, prova di nuovo.', 'error')
            return redirect('/contact')

        nome = request.form['name']
        email = request.form['email']
        oggetto = request.form['subject']
        messaggio = request.form['message']

        # Creazione e invio dell'email
        msg = Message(oggetto,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['info@selenikeart.com'],
                      # Modifica con il tuo indirizzo di destinazione
                      body=f"Da: {nome} <{email}>\n\n{messaggio}")
        mail.send(msg)

        flash('Messaggio inviato con successo!', 'success')
        return redirect('/contact')

    return render_template('contact.html')



def get_images_from_folder(folder, category):
    image_list = []
    for filename in os.listdir(folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join('img/gallery', category, filename)
            image_list.append({'filename': image_path, 'category': category})
    return image_list


@app.route('/art-gallery')
def art_gallery():
    gallery_folder = os.path.join(app.static_folder, 'img/gallery')

    animals_folder = os.path.join(gallery_folder, 'animals')
    comics_folder = os.path.join(gallery_folder, 'comics')
    illustrations_folder = os.path.join(gallery_folder, 'illustrations')

    images = get_images_from_folder(animals_folder, 'animals')
    images += get_images_from_folder(comics_folder, 'comics')
    images += get_images_from_folder(illustrations_folder, 'illustrations')

    return render_template('gallery.html', images=images)

# Rotta per il caricamento delle immagini (protetta)
@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required  # Applica il decorator alla route della dashboard
def upload_image():
    if not session.get('admin_logged_in'):
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('admin_login'))

    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        form.image.data.save(os.path.join(gallery_upload_folder, filename))
        flash('Immagine caricata con successo!', 'success')
        return redirect(url_for('upload_image'))
    return render_template('upload.html', form=form)

# Rotta per la dashboard amministrativa
@app.route('/admin')
@login_required  # Applica il decorator alla route della dashboard
def admin_dashboard():
    return render_template('admin.html')


# Rotta per il login amministrativo
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenziali non valide. Riprova.', 'danger')

    return render_template('login_dashboard.html', form=form)

# Rotta per il logout
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logout effettuato con successo.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/manage-gallery')
def manage_gallery():
    base_path = 'img/gallery'  # Percorso relativo alla root dell'app Flask
    categories = ['animals', 'comics', 'illustrations','altro']
    images = {}
    for category in categories:
        category_path = os.path.join(base_path, category)
        full_path = os.path.join(app.root_path, 'static', category_path)  # Aggiungi 'static' qui
        print("Full path to images:", full_path)  # Debug per confermare il percorso
        if not os.path.exists(full_path):
            print(f"The directory {full_path} does not exist.")
        else:
            images[category] = [{'filename': f, 'path': os.path.join(category_path, f)} for f in os.listdir(full_path) if f.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return render_template('manage_gallery.html', images=images, categories=categories)

@app.route('/delete-image/<category>/<filename>', methods=['POST'])
def delete_image(category, filename):
    file_path = os.path.join('static/img/gallery', category, filename)
    os.remove(file_path)
    return jsonify({'success': True})

@app.route('/move-image', methods=['POST'])
def move_image():
    src_category = request.form['src_category']
    dest_category = request.form['dest_category']
    filename = request.form['filename']
    src_path = os.path.join('static/img/gallery', src_category, filename)
    dest_path = os.path.join('static/img/gallery', dest_category, filename)
    shutil.move(src_path, dest_path)
    return jsonify({'success': True})

@app.route('/admin/security', methods=['GET', 'POST'])
def admin_security():
    if request.method == 'POST':
        # Qui andrebbero gestiti gli aggiornamenti delle impostazioni di sicurezza
        # Ad esempio: aggiornamento della password, configurazione dei permessi, ecc.
        return jsonify({'status': 'success', 'message': 'Impostazioni aggiornate'})
    else:
        # Questo è per il metodo GET, dove si visualizza la pagina
        return render_template('admin_security.html')

@app.route('/admin/security-dashboard')
def security_dashboard():
    log_lines = []
    try:
        with open('access.log', 'r') as log:
            for line in log:
                parts = line.strip().split(' - ')
                app.logger.debug(f'Parsed line with {len(parts)} parts.')
                log_lines.append(line.strip())
    except FileNotFoundError:
        log_lines = ["Nessun log disponibile."]
    except Exception as e:
        log_lines = [f"Errore nella lettura del file di log: {str(e)}"]
    return render_template('security_dashboard.html', log_lines=log_lines)



if __name__ == '__main__':
    app.run(debug=True)
