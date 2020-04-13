from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Schools


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(4, 20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def __init__(self, *k, **kk):
        self._user = None
        super(LoginForm, self).__init__(*k, **kk)

    def validate(self):
        self._user = Schools.query.filter(Schools.username == self.username.data).first()
        return super(LoginForm, self).validate()

    def validate_username(self, field):
        if self._user is None:
            raise ValidationError("Username incorrect.")

    def validate_password(self, field):
        if self._user is not None:
            if not self._user.validate_password(self.password.data):
                raise ValidationError("Password incorrect.")


class WorkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    body = TextAreaField('Description', validators=[DataRequired(), Length(1, 1000)])
