from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired,Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(5, 256)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class WorkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    body = TextAreaField('Description', validators=[DataRequired(), Length(1, 1000)])
