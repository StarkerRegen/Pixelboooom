from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError
from models import User

class SigninForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    email = StringField('EmailAddress', validators=[DataRequired(), Email(message='Email address error.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,16),
        Regexp('^[a-zA-Z0-9]*$', message="The password should contain only a-z, A-z and 0-9." )])
    remember_me = BooleanField('RememberMe', default=False)
    submit = SubmitField('Sign in')

class SignupForm(FlaskForm):
    username = StringField('UserName', validators=[DataRequired(), Length(1,20),
        Regexp('^[a-zA-Z0-9]*$', message="The username should contain only a-z, A-z and 0-9." )])
    email = StringField('EmailAddress', validators=[DataRequired(), Email(message='Email address error.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,16),
        Regexp('^[a-zA-Z0-9]*$', message="The password should contain only a-z, A-z and 0-9." )])
    password_c = PasswordField('Password_c', validators=[DataRequired(), EqualTo('password',message='Password error')])
    submit = SubmitField('Create account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User already exist.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email has been registered, please re-enter')

class ResetForm(FlaskForm):
    username = StringField('UserName', validators=[DataRequired(), Length(1,20),
        Regexp('^[a-zA-Z0-9]*$', message="The username should contain only a-z, A-z and 0-9." )])
    email = StringField('EmailAddress', validators=[DataRequired(), Email(message='Email address error.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,16),
        Regexp('^[a-zA-Z0-9]*$', message="The password should contain only a-z, A-z and 0-9." )])
    password_c = PasswordField('Password_c', validators=[DataRequired(), EqualTo('password',message='Password error')])
    submit = SubmitField('Reset Passwd')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not(user):
            raise ValidationError("User not registered.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not(user):
            raise ValidationError('User not registered.')

class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1,20,message='Length out of limit')])
    category = StringField('category', validators=[DataRequired(), Length(1,50,message='Length out of limit')])
    img = StringField('id', validators=[DataRequired(), Length(1,40,message='Length out of limit')])
    style = StringField('style', validators=[DataRequired(), Length(1,10,message='Length out of limit')])
    article = TextAreaField('style', validators=[DataRequired(), Length(1,120,message='Length out of limit')])
    submit = SubmitField('Publish')

class EditForm(FlaskForm):
    title = StringField('title', validators=[DataRequired(), Length(1,20,message='Length out of limit')])
    category = StringField('category', validators=[DataRequired(), Length(1,50,message='Length out of limit')])
    article = TextAreaField('style', validators=[DataRequired(), Length(1,120,message='Length out of limit')])
    submit = SubmitField('Update')
                                                                        