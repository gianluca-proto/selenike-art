from flask_mail import Mail, Message
from flask import current_app

mail = Mail()  # Crea l'istanza di Mail

def init_mail(app):
    """Inizializza il modulo Flask-Mail con l'app Flask."""
    mail.init_app(app)

def send_email(subject, sender_name, sender_email, message_body):
    """Funzione per inviare email."""
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=['info@selenikeart.com'],
        body=f"Da: {sender_name} <{sender_email}>\n\n{message_body}"
    )
    with current_app.app_context():
        mail.send(msg)
