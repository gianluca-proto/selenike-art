from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired

class CommissionForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    subject = StringField('Oggetto', validators=[DataRequired()])
    drawingType = StringField('Tipo Disegno', validators=[DataRequired()])
    format = StringField('Formato', validators=[DataRequired()])  # ✅ Deve esistere!
    message = TextAreaField('Messaggio', validators=[DataRequired()])
    privacy_consent = StringField('Consenso Privacy', validators=[DataRequired()])
    submit = SubmitField('Invia')
