from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm
from .models import Register


class CustomerRegisterForm(FlaskForm):
    """Registration form for our clients"""
    name = StringField('Name: ')
    username = StringField('Username: ')
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', validators=[
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match!')
    ])
    confirm = PasswordField('Confirm password: ', validators=[validators.DataRequired()])
    country = StringField('Country: ', [validators.DataRequired()])
    state = StringField('State: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip Code: ', [validators.DataRequired()])
    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Upload image only please')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Function to validate username supplied by client"""
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already taken!")
        
    def validate_email(self, email):
        """Function to validate email supplied by client"""
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError("This email address is already taken!")
        

class CustomerLoginForm(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', validators=[
        validators.DataRequired(),
    ])
