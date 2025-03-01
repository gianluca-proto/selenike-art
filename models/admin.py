from models import db  # ✅ Importa db dalla cartella models
from sqlalchemy import Column, Integer, String

class Admin(db.Model):  # ✅ Usa db.Model corretto
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
