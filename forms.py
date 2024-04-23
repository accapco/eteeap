from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField, SelectField, TextAreaField, FieldList, FormField, validators
from flask_wtf.file import FileField, MultipleFileField, FileAllowed

class UserForm(FlaskForm):
    user_type = HiddenField()
    username = StringField('Username', validators=[validators.DataRequired()])
    f_name = StringField('First Name', validators=[validators.DataRequired()])
    m_name = StringField('Middle Name', validators=[validators.DataRequired()])
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

class RequirementForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    description = TextAreaField('Description', validators=[validators.DataRequired()])
    materials = MultipleFileField('Additional Resource(s)')
    submit = SubmitField('Post')

class StatusConfirmationForm(FlaskForm):
    submit = SubmitField('Approve')

class StudentCoursesForm(FlaskForm):
    courses_select = SelectField('Course', choices=[("", "None")], validators=[])
    instructors_select = SelectField('Instructor', choices=[("", "None")], validators=[])
    submit = SubmitField('Enroll')

    def __init__(self, available_courses, available_instructors):
        super().__init__()
        available_courses = [(c['id'], f"{c['code']}: {c['title']}") for c in available_courses]
        available_instructors = [(i['user'], f"{i['l_name'].capitalize()}, {i['f_name']} {i['m_name'][0]}.") for i in available_instructors]
        self.courses_select.choices += available_courses
        self.instructors_select.choices += available_instructors
        self.courses_select.validators = [validators.DataRequired("Course selected is not a valid option.")]
        self.instructors_select.validators = [validators.DataRequired("Select an instructor.")]