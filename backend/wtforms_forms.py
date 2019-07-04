from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required, Length, EqualTo, ValidationError
from models import UserModel
from passlib.hash import pbkdf2_sha512


class RegForm(FlaskForm):
    name = StringField('name', validators = [Required(message = 'Name required')])
    username = StringField('username', validators = [Required(message = 'Username required'), Length(min = 6, max = 20, message = 'Username must be between 6 to 20 characters')])
    password = PasswordField('password', validators = [Required(message = 'Password required')])
    confirm_password = PasswordField('confirm_password', validators = [EqualTo('password', message = 'Passwords must be equal')])
    submit_button = SubmitField('Create User')

    def username_validate(self, username):
        user = UserModel.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('User already exists. Please try a different username')

def invalid_credentials(form, field):
    username = form.username.data
    password = field.data

    user = UserModel.query.filter_by(username = username).first()
    if user is None:
        raise ValidationError('Username or password is incorrect')
    elif not pbkdf2_sha512.verify(password, user.password):
        raise ValidationError('Username or password is incorrect')

class LoginForm(FlaskForm):
    username = StringField('name', validators = [Required(message = 'Username needed')])
    password = PasswordField('password', validators = [Required(message = 'Password needed'), invalid_credentials])
    submit = SubmitField('submit')

    


