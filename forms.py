from flask_wtf import  FlaskForm
from wtforms import SubmitField, SelectField
from flask_wtf.recaptcha import RecaptchaField

class MyForm(FlaskForm):
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

class ChoiceForm(FlaskForm):
    glue_direction = SelectField('Flip Direction', choices=[('hr', 'Horizontal'), ('vr', 'Vertical')])