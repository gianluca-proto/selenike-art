import requests
from flask_mail import Message

from forms.contact_form import ContactForm
from services.cloudinary_service import get_resources
from flask import Blueprint, render_template, request, redirect, flash, \
    url_for, current_app
from services.email_service import send_email, mail
from forms.commission_form import CommissionForm
from services.security_service import limiter

bp = Blueprint('main', __name__)

from flask import Blueprint, render_template
from services.cloudinary_service import get_resources

@bp.route('/')
def home():
    try:
        desktop_images = [img['url'] for img in get_resources('upload', 'img/banner/')]
        mobile_images = [img['url'] for img in get_resources('upload', 'img/banner_mobile/')]
        carousel_animal_images = [img['url'] for img in get_resources('upload', 'img/carousel_animal/')]
        carousel_erotic_images = [img['url'] for img in get_resources('upload', 'img/carousel_erotic/')]
        carousel_comics_images = [img['url'] for img in get_resources('upload', 'img/carousel_comics/')]
        carousel_customized_images = [img['url'] for img in get_resources('upload', 'img/carousel_customized/')]
    except Exception as e:
        desktop_images, mobile_images, carousel_animal_images = [], [], []
        carousel_erotic_images, carousel_comics_images, carousel_customized_images = [], [], []

    return render_template('index.html',
                           carousel_images_desktop=desktop_images,
                           carousel_images_mobile=mobile_images,
                           carousel_animal_images=carousel_animal_images,
                           carousel_erotic_images=carousel_erotic_images,
                           carousel_comics_images=carousel_comics_images,
                           carousel_customized_images=carousel_customized_images)


@bp.route('/about')
def about():
    return render_template('about.html')


@bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def contact():
    form = ContactForm()
    recaptcha_site_key = current_app.config.get('RECAPTCHA_SITE_KEY', '')

    if request.method == 'POST' and form.validate_on_submit():
        recaptcha_response = request.form.get('recaptcha_response')

        if not recaptcha_response:
            flash('Errore di verifica CAPTCHA: nessuna risposta fornita.', 'error')
            return redirect(url_for('main.contact'))

        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': current_app.config.get('RECAPTCHA_SECRET_KEY', ''),
                'response': recaptcha_response
            }
        )
        result = response.json()

        if not result.get('success', False):
            flash('Errore di verifica CAPTCHA.', 'error')
            return redirect(url_for('main.contact'))

        nome = form.name.data
        email = form.email.data
        oggetto = form.subject.data
        messaggio = form.message.data

        msg = Message(
            oggetto,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=['info@selenikeart.com'],
            body=f"Da: {nome} <{email}>\n\n{messaggio}"
        )
        mail.send(msg)

        flash('Messaggio inviato con successo!', 'success')
        return redirect(url_for('main.contact'))

    return render_template('contact.html', form=form, recaptcha_site_key=recaptcha_site_key)



@bp.route('/commissions', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def commissions():
    form = CommissionForm()

    if request.method == 'POST' and form.validate_on_submit():
        nome = form.name.data
        email = form.email.data
        oggetto = form.subject.data
        tipo_disegno = form.drawingType.data
        formato = form.format.data
        messaggio = form.message.data

        # ✅ Usa `send_email()` invece di `mail.send(msg)`
        send_email(oggetto, nome, email, messaggio)

        flash('Messaggio inviato con successo!', 'success')
        return redirect(url_for('main.commissions'))  # Usa il nome del blueprint

    return render_template('commissions.html', form=form)
