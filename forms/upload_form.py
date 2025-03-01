from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class UploadForm(FlaskForm):
    image = FileField('Carica Immagine', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo immagini!')])
    submit = SubmitField('Carica')
