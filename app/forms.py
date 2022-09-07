from dataclasses import field, fields
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('erinnern')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Benutzername *', validators=[DataRequired()])
    email = StringField('E-Mail *', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort *', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen *', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Vorname')
    lastname = StringField('Nachname')
    address = StringField('Adresse')
    phone = StringField('Telefon', validators=[DataRequired()])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte einen anderen Benutzernamen wählen.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte eine andere E-Mail Adresse wählen.')

class EditProfileForm(FlaskForm):
    username = StringField('Benutzername')
    address = StringField('Adresse')
    phone = StringField('Telefon')
    password = PasswordField('Passwort')
    password2 = PasswordField('Passwort wiederholen', validators=[EqualTo('password')])
    submit = SubmitField('Senden')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Bitte einen anderen Benutzernamen wählen.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Passwort zurücksetzen')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Passwort setzen')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PeriodForm(FlaskForm):
    begin = DateField('Von:', default=date.today)
    end = DateField('Bis:', default=date.today)
    submit = SubmitField('Speichern') 
"""
    def validate_end(form):
        if fields.data < form.begin.data:
            raise ValidationError('Das Ende kann nicht vor dem Beginn liegen.')
"""