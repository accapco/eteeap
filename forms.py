from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField, validators
from flask_wtf.file import FileField, FileAllowed

class UserForm(FlaskForm):
    user_type = HiddenField()
    username = StringField('Username', validators=[validators.DataRequired()])
    f_name = StringField('First Name', validators=[validators.DataRequired()])
    m_name = StringField('Middle Name')
    l_name = StringField('Last Name', validators=[validators.DataRequired()])
    password = StringField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Add User')

class DocumentForm(FlaskForm):
    file = FileField('Upload PDF File', validators=[validators.DataRequired(), FileAllowed(['pdf'], 'Only PDF files allowed')])
    submit = SubmitField('Upload')

class ReceiptForm(FlaskForm):
    file = FileField('Upload image file', validators=[validators.DataRequired(), FileAllowed(['png', 'jpg'], 'Only .png and .jpg files allowed')])
    submit = SubmitField('Upload')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    code = StringField('Course Code', validators=[validators.DataRequired()])
    submit = SubmitField('Add Course')

class StatusConfirmationForm(FlaskForm):
    submit = SubmitField('Approve')