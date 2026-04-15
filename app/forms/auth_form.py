from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User, UserRole
import dns.resolver
import re

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(min=2, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register')

    department = StringField('Department')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please login.')
        
        # Domain validation
        try:
            domain = email.data.split('@')[-1]
            dns.resolver.resolve(domain, 'MX')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, Exception):
            raise ValidationError('Invalid email domain. No mail server found.')

    def validate_password(self, field):
        """
        Server-side enforcement of password strength.
        """
        password = field.data
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r"[a-z]", password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r"[A-Z]", password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r"[0-9]", password):
            raise ValidationError('Password must contain at least one digit.')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError('Password must contain at least one special character.')
