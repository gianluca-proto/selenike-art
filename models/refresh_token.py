from .admin import db
from datetime import datetime

class RefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
