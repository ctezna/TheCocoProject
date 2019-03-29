from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
SelectField, DecimalField, IntegerField, TextAreaField, DateField, FileField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from cocoProject.models import User, Coco
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Log In'))

class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    devKey = StringField(_l('Developer Key ID'), validators=[DataRequired()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Username already in use.'))

    def validate_password(self, password):
        if len(password.data) < 8 or len(password.data) > 20:
            raise ValidationError(_l('Please select a password with correct length.'))

class AddCocoForm(FlaskForm):
    name = StringField(_l('Personalized Name'), validators=[DataRequired()])
    img = FileField(_l('Image File'))
    address = StringField(_l('Device Address'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Initialize Connection'))