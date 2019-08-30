from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from cocoProject.models import User, Coco
from flask_wtf.file import FileField, FileAllowed
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
    img = FileField(_l('Coco Profile Picture'), validators=[FileAllowed(['jpg', 'png'])])
    address = StringField(_l('Device Address'), validators=[DataRequired()])
    password = PasswordField(_l('Remote.it Password'), validators=[DataRequired()])
    deviceType = SelectField(_l('Device Type'), choices=[('coco','Coco'), ('horus','Horus')])
    submit = SubmitField(_l('Initialize Connection'))

    # def validate_address(self, address):
    #     coco = Coco.query.filter_by(address=address.data).first()
    #     if coco is not None:
    #         raise ValidationError(_l('Device Address is already registered.'))

class AddRoutineForm(FlaskForm):
    task = RadioField(_l('Choose Task'), choices=[('Dispense Food','Dispense Food'), ('Light','Light')], validators=[DataRequired()])
    mon = BooleanField('M')
    tue = BooleanField('T')
    wed = BooleanField('W')
    thur = BooleanField('Th')
    fri = BooleanField('F')
    sat = BooleanField('S')
    sun = BooleanField('Su')
    days = BooleanField(_l('Select Days'))
    times = StringField(_l('Set Times'), validators=[DataRequired()])
    proxy = StringField('proxy', validators=[DataRequired()])
    submit = SubmitField(_l('Create Routine'))

class EditCocoForm(FlaskForm):
    name = StringField(_l('Change Name'))
    img = FileField(_l('Change Coco Picture'), validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField(_l('Save'))

class EditProfileForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    devKey = StringField(_l('Developer Key ID'))
    submit = SubmitField(_l('Make Changes'))