import logging
import os
from flask import Flask
from config import Config
from routes import main, admin, gallery, security  # ✅ Importa solo i Blueprint giusti
from models import db  # ✅ Importa il database dal modello giusto
from services.email_service import init_mail
from services.security_service import init_limiter
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress


# Creazione dell'app Flask
app = Flask(__name__)
app.config.from_object(Config)

# ✅ Aggiunta della funzione zip a Jinja
app.jinja_env.globals.update(zip=zip)

# ✅ Inizializza i moduli
db.init_app(app)  # ✅ Corretto, usa il database giusto
migrate = Migrate(app, db)
init_mail(app)  # Inizializza Flask-Mail
init_limiter(app)  # Inizializza Flask-Limiter
csrf = CSRFProtect(app)
Compress(app)

# ✅ Registra i Blueprint
app.register_blueprint(main.bp)      # Route principali
app.register_blueprint(admin.bp)      # Route admin
app.register_blueprint(gallery.bp)    # Route galleria
app.register_blueprint(security.bp)   # Route sicurezza

if __name__ == '__main__':
    app.run(debug=True)
