import time
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ✅ Crea l'istanza di Limiter
limiter = Limiter(key_func=get_remote_address)

def init_limiter(app):
    """Inizializza Flask-Limiter con l'app Flask."""
    limiter.init_app(app)



rate_limits = {}

def rate_limit(max_requests, time_window):
    def decorator(f):
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            if ip not in rate_limits:
                rate_limits[ip] = []

            rate_limits[ip] = [t for t in rate_limits[ip] if now - t < time_window]

            if len(rate_limits[ip]) >= max_requests:
                return jsonify({"error": "Too many requests"}), 429

            rate_limits[ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def anonymize_ip(ip):
    return '.'.join(ip.split('.')[:2]) + '.XX.XX'
