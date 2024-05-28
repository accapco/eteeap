from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, SubmitField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, NumberRange
from flask_wtf.file import FileField, MultipleFileField, FileAllowed
from datetime import datetime

class SystemForm(FlaskForm):
    academic_year = IntegerField('Academic Year', validators=[DataRequired("Academic year field cannot be empty.")])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second")], validators=[DataRequired("Semester field cannot be empty.")])
    submit = SubmitField('Save')

class UserForm(FlaskForm):
    user_type = HiddenField()
    username = StringField('Username')
    f_name = StringField('First Name', validators=[DataRequired()])
    m_name = StringField('Middle Name')
    l_name = StringField('Surname', validators=[DataRequired()])
    ext_name = StringField('Ext.')
    citizenship = StringField('Citizenship')
    gender = SelectField("Gender", choices=[('M', 'M'), ('F', 'F')])
    tup_id = StringField('TUP Student ID')
    email = StringField('Email')
    contact_no = StringField('Contact No.')
    address = StringField('Address')
    birthyear = IntegerField('Year')
    birthmonth = IntegerField('Month')
    birthday = IntegerField('Day')
    civil_status = SelectField('Civil Status', choices=[("Single", "Single"), ("Married", "Married"), ("Legally Separated", "Legally Separated"), ("Widowed", "Widowed")])
    password = StringField('One-time Password')
    update = SubmitField('Update Account Details')
    submit = SubmitField('Add User')

    def __init__(self, create=False):
        super().__init__()
        if create == False:
            self.birthyear.validators = [DataRequired(), NumberRange(min=1950, max=datetime.now().year)]
            self.birthmonth.validators = [DataRequired(), NumberRange(min=1, max=12)]
            self.birthday.validators = [DataRequired(), NumberRange(min=1, max=31)]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class FTLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8,message="Password must be at least 8 characters.")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Passwords do not match.")])
    tup_id = StringField('TUP Student ID')
    submit = SubmitField('Save New Password')

    def __init__(self, user_type):
        super().__init__()
        if user_type == 'student':
            self.tup_id.validators = [DataRequired()]

class ChangePasswordForm(FlaskForm):
    current = PasswordField('Current Password', validators=[DataRequired()])
    new = PasswordField('New Password', validators=[DataRequired(), Length(min=8,message="Password must be at least 8 characters.")])
    confirm = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new', "Passwords do not match.")])
    submit = SubmitField('Save New Password')

class DocumentForm(FlaskForm):
    file = FileField('Upload PDF File', validators=[DataRequired(), FileAllowed(['pdf'], 'Only PDF files allowed')])
    submit = SubmitField('Upload')

class ReceiptForm(FlaskForm):
    file = FileField('Upload image file', validators=[DataRequired(), FileAllowed(['png', 'jpg'], 'Only .png and .jpg files allowed')])
    submit = SubmitField('Upload')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    code = StringField('Course Code', validators=[DataRequired()])
    submit = SubmitField('Add Course')

class RequirementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    materials = MultipleFileField('Additional Resource(s)')
    submit = SubmitField('Post')

class GradeSubmissionForm(FlaskForm):
    grade = SelectField('Final Grade', choices=[(1, 1), (1.25, 1.25), (1.5, 1.5), (1.75, 1.75), (2, 2), (2.25, 2.25), (2.5, 2.5), (2.75, 2.75), (3, 3), (5, 5)], validators=[DataRequired()])
    file1 = FileField('Upload File 1', validators=[DataRequired()])
    file2 = FileField('Upload File 2', validators=[DataRequired()])
    file3 = FileField('Upload File 3', validators=[DataRequired()])
    submit = SubmitField('Submit Grade')

class SubmissionForm(FlaskForm):
    submissions = MultipleFileField('Attach File(s)')
    submit = SubmitField('Submit')

class StatusConfirmationForm(FlaskForm):
    submit = SubmitField('Approve')

class StudentProgramForm(FlaskForm):
    academic_year = IntegerField('Acad. Year', validators=[DataRequired("Academic year field cannot be empty.")])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second")], validators=[DataRequired("Semester field cannot be empty.")])
    programs_select =  SelectField('Program', choices=[("", "None")], validators=[DataRequired("Student must be enrolled to a program.")])
    submit = SubmitField('Enroll')

    def __init__(self, programs):
        super().__init__()
        self.programs_select.choices += [(p['id'], p['name']) for p in programs]

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
        self.courses_select.validators = [DataRequired("Course selected is not a valid option.")]
        self.instructors_select.validators = [DataRequired("Select an instructor.")]

class FilterForm(FlaskForm):
    ay = SelectField('Academic Year', choices=[], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second")], validators=[DataRequired()])
    submit = SubmitField('Apply')

    def __init__(self, academic_years):
        super().__init__()
        self.ay.choices = [(a, a) for a in academic_years]