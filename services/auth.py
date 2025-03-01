from functools import wraps

import jwt
import time
from datetime import datetime, timedelta
from flask import current_app, request, flash, redirect, url_for

from models import db
from models.refresh_token import RefreshToken

revoked_tokens = {}

def generate_access_token(user_id):
    exp = datetime.utcnow() + timedelta(minutes=15)
    return jwt.encode({'user_id': user_id, 'exp': exp}, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_jwt(token):
    if not token or token in revoked_tokens:
        return None
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def revoke_token(token):
    revoked_tokens[token] = time.time() + 3600  # Revoca per 1 ora

# Decoratore per proteggere le route con JWT
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('auth_token')
        if not token or not verify_jwt(token):
            flash('Accesso non autorizzato. Effettua il login.', 'danger')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_refresh_token(user_id):
    exp = datetime.utcnow() + timedelta(days=7)
    token = jwt.encode({'user_id': user_id, 'exp': exp}, current_app.secret_key, algorithm='HS256')

    # Salva nel database
    with current_app.app_context():
        db.session.query(RefreshToken).filter_by(user_id=user_id).delete()
        new_token = RefreshToken(user_id=user_id, token=token, expires_at=exp)
        db.session.add(new_token)
        db.session.commit()

    return token