import logging
import os
from flask import Flask, request
from config import Config
from routes import main, admin, gallery, security  # ✅ Importa solo i Blueprint giusti
from models import db  # ✅ Importa il database dal modello giusto
from services.email_service import init_mail
from services.security_service import init_limiter, anonymize_ip
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from dotenv import load_dotenv
import requests
from flask import make_response


# Importa Flask-Babel
from flask_babel import Babel, _

# Carica il file .env
load_dotenv()

def get_server_ip():
    response = requests.get("https://ifconfig.me")
    return response.text

print(f"🌐 IP pubblico del server Heroku: {get_server_ip()}")

# Creazione dell'app Flask
app = Flask(__name__)
app.config.from_object(Config)

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

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


def get_locale():
    # Rileva la lingua preferita dall'utente, ad esempio analizzando la richiesta HTTP.
    return request.accept_languages.best_match(['it', 'en'])

# Inizializza Flask-Babel
babel = Babel(app, locale_selector=get_locale)


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
            "https://cdn.jsdelivr.net/npm/glightbox/dist/css/; "  # <-- Aggiunto qui
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
    return response




@app.after_request
def log_request(response):
    anon_ip = anonymize_ip(request.remote_addr)
    app.logger.info(f"IP: {anon_ip} - Request: {request.method} {request.path} - Response: {response.status_code}")
    return response

# Registra i Blueprint
app.register_blueprint(main.bp)      # Route principali
app.register_blueprint(admin.bp)      # Route admin
app.register_blueprint(gallery.bp)    # Route galleria
app.register_blueprint(security.bp)   # Route sicurezza

if __name__ == '__main__':
    app.run(debug=True)
