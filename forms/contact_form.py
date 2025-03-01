from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Oggetto', validators=[DataRequired()])
    drawingType = StringField('Tipo Disegno', validators=[DataRequired()])
    format = StringField('Formato', validators=[DataRequired()])  # ✅ Aggiunto
    message = TextAreaField('Messaggio', validators=[DataRequired()])
    submit = SubmitField('Invia')
