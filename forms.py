from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField,PasswordField,EmailField
from wtforms.validators import DataRequired,Length,URL

class LoginForm(FlaskForm):
    password = PasswordField('Password:',validators=[DataRequired()])
    email = EmailField('Email:',validators=[DataRequired()])
    submit = SubmitField('Sign in ')

class SignUpForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    password = PasswordField('Password:',validators=[DataRequired()])
    email = EmailField('Email:',validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class AddForm(FlaskForm):
    title = TextAreaField('Title:', validators=[DataRequired(), Length(min=1, max=50)])
    url = TextAreaField('Body:', validators=[DataRequired(), URL()])
    submit = SubmitField('Add Link')
    tags= TextAreaField('Tags:', validators=[DataRequired()])
