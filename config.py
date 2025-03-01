import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or "postgresql://selenike_user:password123@localhost/selenike_art"
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
