import os

from PIL import Image
from dotenv import load_dotenv

# Carica il file .env dal percorso protetto
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'selenike-art-config', '.env'))

class Config:
    SECRET_KEY = os.getenv('APP_SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = (os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")
                               or "postgresql://selenike_user:password123@localhost/selenike_art")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
    RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # Solo HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    PRODUCTION = False

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file):
    try:
        # Verifica se il file è stato effettivamente ricevuto
        print(f"Nome file: {file.filename}")
        print(f"Tipo MIME: {file.mimetype}")

        # Controllo della dimensione manualmente
        file.seek(0, os.SEEK_END)  # Vai alla fine del file
        file_size = file.tell()  # Ottieni la dimensione
        file.seek(0)  # Torna all'inizio

        print(f"Dimensione del file: {file_size} bytes")

        if file_size > MAX_IMAGE_SIZE:
            print("❌ File troppo grande")
            return False  # File troppo grande

        # Controllo che il file sia effettivamente un'immagine
        img = Image.open(file)
        img.verify()
        print("✅ L'immagine è valida!")

        return True
    except Exception as e:
        print(f"❌ Errore nella validazione dell'immagine: {str(e)}")
        return False
