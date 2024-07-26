from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/art-gallery')
def gallery():
    image_folder = os.path.join(app.static_folder, 'img/gallery')
    images = [f for f in os.listdir(image_folder) if
              os.path.isfile(os.path.join(image_folder, f))]
    return render_template('gallery.html', images=images)

@app.route('/commissions')
def commissions():
    return render_template('commissions.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
