from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import Blueprint, render_template, request, redirect, flash, url_for, make_response
from forms.login_form import LoginForm
from models.admin import Admin, db
from models.refresh_token import RefreshToken
from services.security_service import limiter, is_account_locked
from services.auth import verify_jwt, jwt_required, generate_access_token, \
    generate_refresh_token
from flask import current_app as app
import requests  # Assicurati che sia importato in alto nel file
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')  # ✅ Blueprint Admin
# Inizializza Argon2
ph = PasswordHasher()
FAILED_LOGINS = {}

@bp.route('/')
@limiter.limit("5 per minute")  # 5 tentativi al minuto
@jwt_required
def admin_dashboard():
    user_id = verify_jwt(request.cookies.get('auth_token'))  # Ottieni ID utente dal JWT
    if user_id:
        app.logger.info(f"Utente autenticato: ID {user_id}")
        return render_template('admin/admin.html')
    else:
        flash("Sessione scaduta. Effettua di nuovo il login.", "warning")
        return redirect(url_for('admin.admin_login'))


@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    ip = request.remote_addr  # 🔹 Recupera l'IP dell'utente

    # 🔹 Controlla se l'IP è bloccato
    locked, message = is_account_locked(ip)
    if locked:
        flash(message, 'danger')
        return redirect(url_for('admin.admin_login'))

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

                    response = make_response(redirect(url_for('admin.admin_dashboard')))
                    response.set_cookie('auth_token', access_token, httponly=True, secure=True, samesite='Strict')
                    response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='Strict')
                    return response
            except VerifyMismatchError:
                app.logger.warning("Login - Password errata per l'utente {}".format(form.username.data))
                flash('Credenziali non valide.', 'danger')

        else:
            app.logger.warning("Login - Tentativo di accesso con utente inesistente: {}".format(form.username.data))

        flash('Credenziali non valide.', 'danger')
    else:
        # 🔹 Registra il tentativo fallito
        if ip not in FAILED_LOGINS:
            FAILED_LOGINS[ip] = (1, datetime.now())
        else:
            attempts, _ = FAILED_LOGINS[ip]
            FAILED_LOGINS[ip] = (attempts + 1, datetime.now())

    return render_template('admin/login_dashboard.html', form=form, recaptcha_site_key=app.config.get('RECAPTCHA_SITE_KEY', ''))



@bp.route('/logout', methods=['POST'])
@jwt_required
def admin_logout():
    user_id = verify_jwt(request.cookies.get('auth_token'))

    with app.app_context():
        RefreshToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    response = make_response(redirect(url_for('admin.admin_login')))
    response.set_cookie('auth_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)
    flash('Logout effettuato.', 'success')
    return response
