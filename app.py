from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'tuo_segreto'  # Necessario per visualizzare messaggi di conferma

# Configurazione email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gianlucaproto@gmail.com'
app.config['MAIL_PASSWORD'] = 'ziojaemccrrjydyp'

mail = Mail(app)  # Corretta inizializzazione


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/commissions')
def commissions():
    return render_template('commissions.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nome = request.form['name']
        email = request.form['email']
        oggetto = request.form['subject']
        tipo_disegno = request.form['drawingType']
        formato = request.form['format']
        messaggio = request.form['message']

        msg = Message(oggetto,
                      sender=email,
                      recipients=["info@selenikeart.com"])
        msg.body = f"""
        Da: {nome} <{email}>
        Tipo di Disegno: {tipo_disegno}
        Formato: {formato}

        {messaggio}
        """
        mail.send(msg)
        flash('Email inviata con successo!', 'success')
        return redirect('/contact')

    return render_template('contact.html')


def get_images_from_folder(folder, category):
    image_list = []
    for filename in os.listdir(folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join('img/gallery', category, filename)
            image_list.append({'filename': image_path, 'category': category})
    return image_list


@app.route('/art-gallery')
def art_gallery():
    gallery_folder = os.path.join(app.static_folder, 'img/gallery')

    animals_folder = os.path.join(gallery_folder, 'animals')
    comics_folder = os.path.join(gallery_folder, 'comics')
    illustrations_folder = os.path.join(gallery_folder, 'illustrations')

    images = get_images_from_folder(animals_folder, 'animals')
    images += get_images_from_folder(comics_folder, 'comics')
    images += get_images_from_folder(illustrations_folder, 'illustrations')

    return render_template('gallery.html', images=images)


if __name__ == '__main__':
    app.run(debug=True)
