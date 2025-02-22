import logging
import os
import shutil
from functools import wraps
from logging.handlers import RotatingFileHandler
import requests
from flask import Flask, render_template, request, redirect, flash, url_for, \
    session, jsonify
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.api import resources_by_tag, delete_resources_by_tag, resources
from flask_compress import Compress

cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('CLOUD_API_KEY'),
    api_secret = os.getenv('CLOUD_API_SECRET')
)

app = Flask(__name__)
Compress(app)
app.secret_key = os.getenv('APP_SECRET_KEY')  # Necessario per visualizzare messaggi di conferma
app.config['PRODUCTION'] = False  # Imposta a True in produzione
app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
# Aggiungi zip all'environment Jinja
app.jinja_env.globals.update(zip=zip)

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
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)  # Corretta inizializzazione

# Dummy dati di login per l'amministratore
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


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

def get_resources(tipo, prefix):
    response_desktop = cloudinary.api.resources(
        type=tipo,
        prefix=prefix,
        max_results=10
    )
    return response_desktop

@app.route('/')
def home():
    try:
        # Carica immagini per desktop
        response_desktop = get_resources('upload', 'img/banner/')
        desktop_images = [img['secure_url'] for img in response_desktop.get('resources', [])]

        # Carica immagini per mobile
        response_mobile = get_resources('upload', 'img/banner_mobile/')
        mobile_images = [img['secure_url'] for img in response_mobile.get('resources', [])]

        response_carousel_animal = get_resources('upload', 'img/carousel_animal/')
        carousel_animal_images = [img['secure_url'] for img in response_carousel_animal.get('resources', [])]

        response_carousel_erotic = get_resources('upload','img/carousel_erotic/')
        carousel_erotic_images = [img['secure_url'] for img in response_carousel_erotic.get('resources',[])]
        app.logger.info(f"Desktop images loaded: {desktop_images}")
        app.logger.info(f"Mobile images loaded: {mobile_images}")
        app.logger.info(f"Carousel Animal images loaded: {carousel_animal_images}")
    except Exception as e:
        app.logger.error(f"Failed to load images from Cloudinary: {str(e)}")
        desktop_images = []
        mobile_images = []
        carousel_animal_images = []
        carousel_erotic_images = []
    return render_template('index.html',
                           carousel_images_desktop=desktop_images,
                           carousel_images_mobile=mobile_images,
                           carousel_animal_images=carousel_animal_images,
                           carousel_erotic_images=carousel_erotic_images)



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


@app.route('/art-gallery')
def art_gallery():
    categories = ['animals', 'comics', 'illustrations']
    images = []
    for category in categories:
        res = cloudinary.api.resources(
            type='upload',
            prefix=f'img/gallery/{category}/',
            max_results=100
        )
        for img in res.get('resources', []):
            images.append({
                'filename': img['public_id'],
                'url': img['secure_url'],
                'category': category
            })

    return render_template('gallery.html', images=images)





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

class UploadForm(FlaskForm):
    image = FileField('Image File', validators=[DataRequired()])

# Rotta per il caricamento delle immagini (protetta)
@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
def upload_image():
    if not session.get('admin_logged_in'):
        flash('Per favore, effettua il login per accedere a questa pagina.', 'warning')
        return redirect(url_for('admin_login'))
    form = UploadForm()
    if form.validate_on_submit():
        file_to_upload = form.image.data
        filename = secure_filename(file_to_upload.filename)
        # Carica l'immagine su Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_to_upload,
            folder='img/gallery/altro',
            format='webp'
        )
        if upload_result.get('secure_url'):
            flash('Immagine caricata con successo su Cloudinary!', 'success')
            return redirect(url_for('upload_image'))
        else:
            flash('Caricamento non riuscito.', 'danger')
    return render_template('upload.html', form=form)

@app.route('/manage-gallery')
def manage_gallery():
    categories = ['animals', 'comics', 'illustrations', 'altro']
    images = {}
    for category in categories:
        # Assicurati che 'prefix' sia correttamente specificato
        res = cloudinary.api.resources(type='upload', prefix=f'img/gallery/{category}/', max_results=100)
        if res.get('resources'):
            images[category] = [{'filename': img['public_id'], 'url': img['secure_url']} for img in res['resources']]
        else:
            print(f"No images found in category: {category}")
            images[category] = []
    return render_template('manage_gallery.html', images=images, categories=categories)

@app.route('/delete-image/<path:public_id>', methods=['POST'])
def delete_image(public_id):
    try:
        # Assicurati che il public_id sia corretto e non includa l'estensione del file
        response = cloudinary.uploader.destroy(public_id, invalidate=True)
        if response.get('result') == 'ok':
            return jsonify({'success': True, 'message': 'Image deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete image'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/move-image', methods=['POST'])
def move_image():
    src_public_id = request.form.get('src_public_id')
    dest_public_id = request.form.get('dest_public_id')
    try:
        response = cloudinary.uploader.rename(src_public_id, dest_public_id)
        if 'error' in response:
            return jsonify({'success': False, 'message': response['error']['message']}), 500
        return jsonify({'success': True, 'message': 'Image moved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




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
