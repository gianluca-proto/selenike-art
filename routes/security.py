from flask import Blueprint, render_template, current_app
import os

bp = Blueprint('security', __name__)

@bp.route('/antro-1986/security-dashboard')
def security_dashboard():
    log_lines = []
    try:
        with open('logs/access.log', 'r') as log:
            log_lines = log.readlines()
    except FileNotFoundError:
        log_lines = ["Nessun log disponibile."]
    return render_template('antro-1986/security_dashboard.html', log_lines=log_lines)
