import logging
import os
from functools import wraps
from logging.handlers import RotatingFileHandler
import requests
from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from flask_mail import Mail, Message
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask_compress import Compress
from wtforms import TextAreaField, EmailField
from datetime import timedelta
from PIL import Image
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import request, redirect, url_for, flash, render_template, make_response
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import time
from flask import make_response
from flask import request, jsonify
from flask_migrate import Migrate


rate_limits = {}  # Memorizza i tentativi di accesso per IP


app = Flask(__name__)


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)

limiter.init_app(app)


class ContactForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Oggetto', validators=[DataRequired()])
    drawingType = StringField('Tipo Disegno', validators=[DataRequired()])
    format = StringField('Formato', validators=[DataRequired()])
    message = TextAreaField('Messaggio', validators=[DataRequired()])
    privacy_consent = StringField('Consenso Privacy', validators=[DataRequired()])
    submit = SubmitField('Invia')




# Configurazione Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUD_NAME'),
    api_key=os.getenv('CLOUD_API_KEY'),
    api_secret=os.getenv('CLOUD_API_SECRET')
)

app = Flask(__name__)
csrf = CSRFProtect(app)  # Abilita CSRF Protection
Compress(app)
app.secret_key = os.getenv('APP_SECRET_KEY')
app.config['PRODUCTION'] = False
# Sicurezza sessioni e cookie
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Solo HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Protezione CSRF con chiave segreta
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('CSRF_SECRET_KEY', 'True')

# Ora Flask può accedere alla variabile
app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY', 'default_value')

app.jinja_env.globals.update(zip=zip)

# Configurazione del logger
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('access.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

limiter = Limiter(key_func=get_remote_address)  # Rimuovi "app"
limiter.init_app(app)  # Inizializza Flask-Limiter con l'app

from flask_sqlalchemy import SQLAlchemy
# Prendi l'URL del database dall'ambiente
DATABASE_URL = os.getenv('DATABASE_URL')

# Se non trova la variabile, usa il database locale
if not DATABASE_URL:
    DATABASE_URL = os.getenv('DATABASE_URL_LOCAL')
    print("⚠️ DATABASE_URL non trovato, uso PostgreSQL locale")

# Se ancora non è definito, usa un database locale come fallback
if not DATABASE_URL:
    DATABASE_URL = "postgresql://selenike_user:password123@localhost/selenike_art"
    print("⚠️ DATABASE_URL non trovato, uso PostgreSQL locale")

# Corregge il formato dell'URL se viene da Heroku
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


def rate_limit(max_requests, time_window):
    def decorator(f):
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            if ip not in rate_limits:
                rate_limits[ip] = []

            # Rimuove richieste vecchie
            rate_limits[ip] = [t for t in rate_limits[ip] if
                               now - t < time_window]

            if len(rate_limits[ip]) >= max_requests:
                return jsonify({"error": "Too many requests"}), 429

            rate_limits[ip].append(now)
            return f(*args, **kwargs)

        return wrapped

    return decorator

# Funzione per generare un JWT
def generate_jwt(user_id):
    expiration = datetime.utcnow() + timedelta(hours=1)  # ✅ CORRETTO
    return jwt.encode({'user_id': user_id, 'exp': expiration}, app.secret_key, algorithm='HS256')


revoked_tokens = {}  # Dizionario per gestire i token revocati

def revoke_token(token):
    revoked_tokens[token] = time.time() + 3600  # Revoca il token per 1 ora


def verify_jwt(token):
    if not token or (token in revoked_tokens and time.time() > revoked_tokens[token]):
        return None  # Token non valido o revocato
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# Decoratore per proteggere le route con JWT
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token or not verify_jwt(token):
            flash('Accesso non autorizzato. Effettua il login.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function



MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()
        if file.content_length > MAX_IMAGE_SIZE:
            return False  # File troppo grande
        return True
    except Exception:
        return False


# Funzione per anonimizzare IP nei log
def anonymize_ip(ip):
    return '.'.join(ip.split('.')[:2]) + '.XX.XX'

@app.after_request
def log_request(response):
    anon_ip = anonymize_ip(request.remote_addr)
    app.logger.info(f"IP: {anon_ip} - Request: {request.method} {request.path} - Response: {response.status_code}")
    return response

# Configurazione email
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

# Protezione login con password hashata
# Rimuovere queste due righe:
# ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
# ADMIN_PASSWORD_HASHED = generate_password_hash(os.getenv('ADMIN_PASSWORD'))

import secrets

# Creazione Admin alla prima esecuzione
def initialize_admin():
    with app.app_context():
        admin = Admin.query.filter_by(username="admin").first()
        if not admin:
            default_password = os.getenv('ADMIN_PASSWORD', secrets.token_urlsafe(16))
            hashed_password = generate_password_hash(default_password)
            new_admin = Admin(username="admin", password_hash=hashed_password)
            db.session.add(new_admin)
            db.session.commit()
            app.logger.warning(f"Admin creato con password: {default_password}")

#initialize_admin()



# Configurazione del percorso per il caricamento delle immagini
gallery_upload_folder = os.path.join('static', 'img', 'gallery/altro')
if not os.path.exists(gallery_upload_folder):
    os.makedirs(gallery_upload_folder)


# Form di Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    image = FileField('Carica Immagine', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo immagini!')])
    submit = SubmitField('Carica')


from dotenv import load_dotenv

load_dotenv()
app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')

# Protezione CSP e headers HTTP
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' https://www.google.com https://www.gstatic.com https://www.recaptcha.net; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdn.jsdelivr.net/npm/ "
        "https://cdnjs.cloudflare.com https://cdn.iubenda.com https://www.google.com https://www.gstatic.com "
        "https://cdnjs.cloudflare.com/ajax/libs/ekko-lightbox/5.3.0/ https://www.gstatic.com/recaptcha/; "
        "style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com "
        "https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.css https://fonts.googleapis.com https://cdn.iubenda.com; "
        "style-src-elem 'self' 'unsafe-inline' https://cdn.iubenda.com https://stackpath.bootstrapcdn.com "
        "https://cdnjs.cloudflare.com https://cdn.jsdelivr.net/npm/swiper/; "
        "img-src 'self' https://res.cloudinary.com data: https://www.google.com https://www.gstatic.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com https://fonts.googleapis.com data: blob: application/font-woff application/font-woff2; "
        "frame-src 'self' https://www.google.com/recaptcha/ https://www.recaptcha.net/ https://www.gstatic.com/recaptcha/ https://www.google.com; "
        "connect-src 'self' https://res.cloudinary.com https://fonts.googleapis.com https://fonts.gstatic.com "
        "https://cdn.jsdelivr.net https://www.google.com https://www.gstatic.com https://www.recaptcha.net;"
    )

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response






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

        response_carousel_comics = get_resources('upload','img/carousel_comics/')
        carousel_comics_images = [img['secure_url'] for img in response_carousel_comics.get('resources',[])]

        response_carousel_customized = get_resources('upload',
                                                     'img/carousel_customized/')
        carousel_customized_images = [img['secure_url'] for img in
                                      response_carousel_customized.get('resources',
                                                                       [])]

        app.logger.info(f"Desktop images loaded: {desktop_images}")
        app.logger.info(f"Mobile images loaded: {mobile_images}")
        app.logger.info(f"Carousel Animal images loaded: {carousel_animal_images}")
    except Exception as e:
        app.logger.error(f"Failed to load images from Cloudinary: {str(e)}")
        desktop_images = []
        mobile_images = []
        carousel_animal_images = []
        carousel_erotic_images = []
        carousel_comics_images = []
        carousel_customized_images = []
    return render_template('index.html',
                           carousel_images_desktop=desktop_images,
                           carousel_images_mobile=mobile_images,
                           carousel_animal_images=carousel_animal_images,
                           carousel_erotic_images=carousel_erotic_images,
                           carousel_comics_images=carousel_comics_images,
                           carousel_customized_images=carousel_customized_images)


from wtforms import TextAreaField, EmailField

class CommissionForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Oggetto', validators=[DataRequired()])
    drawingType = StringField('Tipo Disegno', validators=[DataRequired()])
    format = StringField('Formato', validators=[DataRequired()])
    message = TextAreaField('Messaggio', validators=[DataRequired()])
    privacy_consent = StringField('Consenso Privacy', validators=[DataRequired()])
    submit = SubmitField('Invia')

@limiter.limit("3 per minute")
@app.route('/commissions', methods=['GET', 'POST'])
def commissions():
    form = CommissionForm()

    if request.method == 'POST' and form.validate_on_submit():
        nome = form.name.data
        email = form.email.data
        oggetto = form.subject.data
        tipo_disegno = form.drawingType.data
        formato = form.format.data
        messaggio = form.message.data
        consenso = form.privacy_consent.data

        # Creazione e invio dell'email
        msg = Message(oggetto,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['info@selenikeart.com'],
                      body=f"Da: {nome} <{email}>\n\nTipo Disegno: {tipo_disegno}\nFormato: {formato}\n\n{messaggio}")
        mail.send(msg)

        flash('Messaggio inviato con successo!', 'success')
        return redirect('/commissions')

    return render_template('commissions.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')

@limiter.limit("3 per minute")
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    for field in form:
        app.logger.info(
            f"🔍 {field.name} -> {field.data}, valid? {field.validate(form)}")

    recaptcha_response = None  # ✅ Inizializza la variabile


    if request.method == 'POST' and form.validate_on_submit():
        recaptcha_response = request.form.get('recaptcha_response')

        # 🔹 Log del token ricevuto
        app.logger.info(f"Contact - Received reCAPTCHA token: {recaptcha_response}")

        if not recaptcha_response:
            app.logger.error("Contact - Nessun token reCAPTCHA ricevuto!")
            flash('Errore di verifica CAPTCHA: nessuna risposta fornita.', 'error')
            return redirect('/contact')

        # 🔹 Verifica reCAPTCHA con Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': app.config.get('RECAPTCHA_SECRET_KEY', ''),  # Secret Key
                'response': recaptcha_response
            }
        )
        result = response.json()

        # 🔹 Log della risposta di Google
        app.logger.info(f"Contact - Google reCAPTCHA response: {result}")

        if not result.get('success', False):
            app.logger.error(f"Contact - Errore reCAPTCHA: {result.get('error-codes')}")
            flash(f"Errore di verifica CAPTCHA: {result.get('error-codes')}", 'error')
            return redirect('/contact')

        if result.get('score', 0) < 0.5:
            app.logger.warning("Contact - CAPTCHA score troppo basso, possibile bot.")
            flash('Errore di verifica CAPTCHA, prova di nuovo.', 'error')
            return redirect('/contact')

        # ✅ CAPTCHA SUPERATO - Processiamo il modulo
        nome = form.name.data
        email = form.email.data
        oggetto = form.subject.data
        messaggio = form.message.data
        tipo_disegno = form.drawingType.data
        formato = form.format.data
        consenso = form.privacy_consent.data

        # 🔹 Creazione e invio dell'email
        msg = Message(
            oggetto,
            sender=app.config['MAIL_USERNAME'],
            recipients=['info@selenikeart.com'],
            body=f"Da: {nome} <{email}>\n\nTipo Disegno: {tipo_disegno}\nFormato: {formato}\n\n{messaggio}"
        )
        mail.send(msg)

        flash('Messaggio inviato con successo!', 'success')
        return redirect('/contact')

    return render_template('contact.html', form=form, recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY', ''))





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




@limiter.limit("5 per minute")  # 5 tentativi al minuto
@app.route('/admin')
@jwt_required
def admin_dashboard():
    user_id = verify_jwt(request.cookies.get('auth_token'))  # Ottieni ID utente dal JWT
    if user_id:
        app.logger.info(f"Utente autenticato: ID {user_id}")
        return render_template('admin.html')
    else:
        flash("Sessione scaduta. Effettua di nuovo il login.", "warning")
        return redirect(url_for('admin_login'))



from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta

# Memorizzazione dei tentativi di login falliti
FAILED_LOGINS = {}

def is_account_locked(ip):
    """Controlla se un IP è temporaneamente bloccato per troppi tentativi di login."""
    if ip in FAILED_LOGINS:
        attempts, last_attempt = FAILED_LOGINS[ip]
        if attempts >= 20 and datetime.now() - last_attempt < timedelta(hours=2):
            return True, "Troppi tentativi. Riprova tra 2 ore."
        elif attempts >= 10 and datetime.now() - last_attempt < timedelta(minutes=30):
            return True, "Troppi tentativi. Riprova tra 30 minuti."
        elif attempts >= 5 and datetime.now() - last_attempt < timedelta(minutes=5):
            return True, "Troppi tentativi. Riprova tra 5 minuti."
    return False, None

class RefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

# Funzioni per gestire JWT
def generate_access_token(user_id):
    exp = datetime.utcnow() + timedelta(minutes=15)
    return jwt.encode({'user_id': user_id, 'exp': exp}, app.secret_key, algorithm='HS256')

def generate_refresh_token(user_id):
    exp = datetime.utcnow() + timedelta(days=7)
    token = jwt.encode({'user_id': user_id, 'exp': exp}, app.secret_key, algorithm='HS256')

    # Salva nel database
    with app.app_context():
        db.session.query(RefreshToken).filter_by(user_id=user_id).delete()
        new_token = RefreshToken(user_id=user_id, token=token, expires_at=exp)
        db.session.add(new_token)
        db.session.commit()

    return token


def verify_jwt(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# Decoratore per proteggere le rotte
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        user_id = verify_jwt(token)
        if not user_id:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function



# Inizializza Argon2
ph = PasswordHasher()


@limiter.limit("5 per minute")
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        recaptcha_response = request.form.get('recaptcha_response')

        # 🔹 Log del token reCAPTCHA
        app.logger.info(f"Login - Received reCAPTCHA token: {recaptcha_response}")

        if not recaptcha_response:
            app.logger.error("Login - Nessun token reCAPTCHA ricevuto!")
            flash('Errore CAPTCHA: nessuna risposta fornita.', 'danger')
            return redirect(url_for('admin_login'))

        # 🔹 Verifica reCAPTCHA con Google
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': app.config.get('RECAPTCHA_SECRET_KEY', ''),  # Secret Key
                'response': recaptcha_response
            }
        )
        result = response.json()

        # 🔹 Log della risposta di Google
        app.logger.info(f"Login - Google reCAPTCHA response: {result}")

        if not result.get('success', False):
            app.logger.error(f"Login - Errore reCAPTCHA: {result.get('error-codes')}")
            flash(f"Errore CAPTCHA: {result.get('error-codes')}", 'danger')
            return redirect(url_for('admin_login'))

        if result.get('score', 0) < 0.5:
            app.logger.warning("Login - CAPTCHA score troppo basso, possibile bot.")
            flash('Errore CAPTCHA. Sei sicuro di non essere un bot?', 'danger')
            return redirect(url_for('admin_login'))

        # ✅ CAPTCHA SUPERATO - Controlliamo il database
        admin = Admin.query.filter_by(username=form.username.data).first()

        if admin:
            try:
                # 🔹 Verifica della password con Argon2
                if ph.verify(admin.password_hash, form.password.data):
                    access_token = generate_access_token(admin.id)
                    refresh_token = generate_refresh_token(admin.id)

                    response = make_response(redirect(url_for('admin_dashboard')))
                    response.set_cookie('auth_token', access_token, httponly=True, secure=True, samesite='Strict')
                    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')
                    return response
            except VerifyMismatchError:
                app.logger.warning("Login - Password errata per l'utente {}".format(form.username.data))
                flash('Credenziali non valide.', 'danger')

        else:
            app.logger.warning("Login - Tentativo di accesso con utente inesistente: {}".format(form.username.data))

        flash('Credenziali non valide.', 'danger')

    return render_template('login_dashboard.html', form=form, recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY', ''))



@app.route('/admin/refresh-token', methods=['POST'])
def refresh_token():
    refresh_token = request.cookies.get('refresh_token')
    user_id = verify_jwt(refresh_token)

    # Controlla il token nel database
    token_entry = RefreshToken.query.filter_by(user_id=user_id, token=refresh_token).first()
    if not token_entry:
        return jsonify({"message": "Token non valido o scaduto"}), 401

    new_access_token = generate_access_token(user_id)
    response = jsonify({"message": "Access token rinnovato"})
    response.set_cookie('auth_token', new_access_token, httponly=True, secure=True, samesite='Strict')
    return response


# Logout
@app.route('/admin/logout', methods=['POST'])
@jwt_required
def admin_logout():
    user_id = verify_jwt(request.cookies.get('auth_token'))

    # Cancella il refresh token dal database
    with app.app_context():
        RefreshToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    response = make_response(redirect(url_for('admin_login')))
    response.set_cookie('auth_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    flash('Logout effettuato.', 'success')
    return response





@limiter.limit("2 per minute")  # Massimo 2 upload al minuto
@app.route('/admin/upload', methods=['GET', 'POST'])
@jwt_required
@csrf.exempt
def upload_image():
    form = UploadForm()
    if form.validate_on_submit():
        file_to_upload = form.image.data
        if not validate_image(file_to_upload):
            flash('File non valido. Assicurati di caricare un immagine corretta.', 'danger')
            return redirect(url_for('upload_image'))

        filename = secure_filename(file_to_upload.filename)
        upload_result = cloudinary.uploader.upload(file_to_upload, folder='img/gallery/altro', format='webp')

        if upload_result.get('secure_url'):
            flash('Immagine caricata con successo!', 'success')
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

@limiter.limit("5 per minute")  # Protegge da abusi nella cancellazione
@app.route('/delete-image/<path:public_id>', methods=['POST'])
@jwt_required
@csrf.exempt
def delete_image(public_id):
    user_id = verify_jwt(request.cookies.get('auth_token'))  # 🔹 Recupera ID admin dal JWT
    admin = Admin.query.get(user_id)  # 🔹 Ottiene l'admin dal database

    if not admin:
        return jsonify({'success': False, 'message': 'Azione non autorizzata'}), 403

    try:
        response = cloudinary.uploader.destroy(public_id, invalidate=True)
        if response.get('result') == 'ok':
            app.logger.info(f"IMAGE DELETED: Admin {admin.username} ha eliminato l'immagine {public_id}")
            return jsonify({'success': True, 'message': 'Image deleted successfully'})
        else:
            app.logger.warning(f"IMAGE DELETE FAILED: Admin {admin.username} ha tentato di eliminare {public_id}, ma è fallito.")
            return jsonify({'success': False, 'message': 'Failed to delete image'})
    except Exception as e:
        app.logger.error(f"IMAGE DELETE ERROR: Errore durante l'eliminazione dell'immagine {public_id} da parte di {admin.username}. Errore: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500





@app.route('/move-image', methods=['POST'])
@jwt_required  # 🔹 Protezione con JWT invece di Flask-Login
@csrf.exempt
def move_image():
    user_id = verify_jwt(request.cookies.get('auth_token'))  # 🔹 Recupera ID admin dal JWT
    admin = Admin.query.get(user_id)  # 🔹 Ottiene l'admin dal database

    if not admin:
        return jsonify({'success': False, 'message': 'Azione non autorizzata'}), 403

    src_public_id = request.form.get('src_public_id')
    dest_public_id = request.form.get('dest_public_id')

    try:
        response = cloudinary.uploader.rename(src_public_id, dest_public_id)
        if 'error' in response:
            app.logger.warning(f"IMAGE MOVE FAILED: Admin {admin.username} ha tentato di spostare {src_public_id} in {dest_public_id}, ma è fallito.")
            return jsonify({'success': False, 'message': response['error']['message']}), 500
        app.logger.info(f"IMAGE MOVED: Admin {admin.username} ha spostato l'immagine da {src_public_id} a {dest_public_id}")
        return jsonify({'success': True, 'message': 'Image moved successfully'})
    except Exception as e:
        app.logger.error(f"IMAGE MOVE ERROR: Errore durante lo spostamento di {src_public_id} in {dest_public_id} da parte di {admin.username}. Errore: {str(e)}")
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
