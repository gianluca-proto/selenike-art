import logging
from datetime import datetime

from flask import Flask, request, send_from_directory
from config import Config # ✅ Importa solo i Blueprint giusti
from models import db  # ✅ Importa il database dal modello giusto
from services.email_service import init_mail
from services.security_service import init_limiter
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from dotenv import load_dotenv
import requests
from extensions import cache  # usa istanza globale
from apscheduler.schedulers.background import BackgroundScheduler
from services.cloudinary_service import sync_logs_with_cloudinary, sync_files_with_cloudinary
from log_utils import write_log_line




# Importa Flask-Babel
from flask_babel import Babel

# Carica il file .env
load_dotenv()

def get_server_ip():
    response = requests.get("https://ifconfig.me")
    return response.text

print(f"🌐 IP pubblico del server Heroku: {get_server_ip()}")

# Creazione dell'app Flask
app = Flask(__name__)
app.config.from_object(Config)
cache.init_app(app, config={'CACHE_TYPE': 'simple'})   # inizializza istanza globale
# Imposta la lingua predefinita se non definita in Config
app.config.setdefault('BABEL_DEFAULT_LOCALE', 'it')
# Cartella per le traduzioni (assicurati che esista e contenga i file .mo compilati)
app.config.setdefault('BABEL_TRANSLATION_DIRECTORIES', 'translations')

# Aggiunta della funzione zip a Jinja
app.jinja_env.globals.update(zip=zip)

# Inizializza i moduli
db.init_app(app)  # ✅ Usa il database giusto
migrate = Migrate(app, db)
init_mail(app)    # Inizializza Flask-Mail
init_limiter(app) # Inizializza Flask-Limiter
csrf = CSRFProtect(app)
Compress(app)
from flask import make_response

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = make_response(send_from_directory('static', filename))
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


def get_locale():
    # Rileva la lingua preferita dall'utente, ad esempio analizzando la richiesta HTTP.
    return request.accept_languages.best_match(['it', 'en'])

# Inizializza Flask-Babel
babel = Babel(app, locale_selector=get_locale)


# Imposta header di sicurezza su tutte le risposte
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' https://www.google.com https://www.gstatic.com https://www.recaptcha.net; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdn.jsdelivr.net/npm/ "
            "https://cdnjs.cloudflare.com https://cdn.iubenda.com https://www.google.com https://www.gstatic.com "
            "https://cdnjs.cloudflare.com/ajax/libs/ekko-lightbox/5.3.0/ https://www.gstatic.com/recaptcha/; "
        "style-src 'self' 'unsafe-inline' https://cdn.iubenda.com https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com "
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/ https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.css "
            "https://fonts.googleapis.com https://cdn.iubenda.com https://cdn.jsdelivr.net/npm/glightbox/dist/css/; "  # <-- Aggiunto qui
        "style-src-elem 'self' 'unsafe-inline' https://cdn.iubenda.com https://stackpath.bootstrapcdn.com https://cdnjs.cloudflare.com "
            "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/ https://cdn.jsdelivr.net/npm/swiper/ "
            "https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.css https://fonts.googleapis.com https://cdn.iubenda.com "
            "https://cdn.jsdelivr.net/npm/glightbox/dist/css/; "  
        "img-src 'self' https://res.cloudinary.com data: https://www.google.com https://www.gstatic.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com https://fonts.googleapis.com data: blob: application/font-woff application/font-woff2; "
        "frame-src 'self' https://www.google.com/recaptcha/ https://www.recaptcha.net/ https://www.gstatic.com/recaptcha/ "
            "https://www.google.com https://www.iubenda.com; " 
        "connect-src 'self' https://res.cloudinary.com https://fonts.googleapis.com https://fonts.gstatic.com "
            "https://cdn.jsdelivr.net https://www.google.com https://www.gstatic.com https://www.recaptcha.net;"
    )
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Permissions-Policy'] = 'geolocation=(), camera=(), microphone=()'
    return response




# Configurazione logging accessi (sempre attiva)
# RIMOSSA CloudinaryRotatingFileHandler e RotatingFileHandler

@app.after_request
def log_access(response):
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or '0.0.0.0'
    user_agent = request.user_agent.string or 'N/A'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    log_line = f"{timestamp} - {ip} - {response.status} - {request.path} - {user_agent}"
    write_log_line(log_line)
    return response

# Importa i Blueprint una sola volta, dopo l'inizializzazione dell'app e delle estensioni
from routes import main, admin, gallery, security

# Registra i Blueprint
app.register_blueprint(main.bp)      # Route principali
app.register_blueprint(admin.bp)      # Route admin
app.register_blueprint(gallery.bp)    # Route galleria
app.register_blueprint(security.bp)   # Route sicurezza

# Avvia il job di sincronizzazione automatica ogni 5 minuti
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(lambda: sync_logs_with_cloudinary(log_dir=".", pattern="access.log", folder="logs"), 'interval', minutes=5, id='sync_logs')
scheduler.add_job(lambda: sync_files_with_cloudinary(local_dir=".", pattern="*.csv", folder="stats"), 'interval', minutes=5, id='sync_csv')
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
