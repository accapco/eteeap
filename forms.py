from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, SubmitField, SelectField, RadioField, BooleanField, TextAreaField, PasswordField, FieldList, FormField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, NumberRange
from flask_wtf.file import FileField, MultipleFileField, FileAllowed
from datetime import datetime

class SystemForm(FlaskForm):
    academic_year = StringField('Academic Year', validators=[DataRequired("Academic year field cannot be empty."), Regexp(regex=r"20\d{2}-20\d{2}", message="Invalid academic year format.")])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired("Semester field cannot be empty.")])
    submit = SubmitField('Save')

class EducationalBackgroundForm(FlaskForm):
    id = HiddenField()
    school = StringField('University')
    degree = StringField('Degree (Write in Full)')
    start_year = IntegerField('Year Started')
    end_year = IntegerField('Year Graduated')
    academic_honors = StringField('Academic Honors')
    submit = SubmitField("Add")
    update = SubmitField("Update")

class NewAccountForm(FlaskForm):
    user_type = HiddenField()
    username = StringField('Username')
    f_name = StringField('First Name', validators=[DataRequired()])
    m_name = StringField('Middle Name')
    l_name = StringField('Surname', validators=[DataRequired()])
    ext_name = StringField('Ext.')
    gender = SelectField("Gender", choices=[('M', 'M'), ('F', 'F')])
    tup_id = StringField('TUP Student ID')
    college = SelectField("Assigned College", choices=[("COS", "College of Science"), ("CIE", "College of Industrial Education"), ("CIT", "College of Industrial Technology")], default='COS')
    password = StringField('One-time Password')
    submit = SubmitField('Add User')

class UserAccountForm(FlaskForm):
    user_type = HiddenField()
    username = StringField('Username')
    f_name = StringField('First Name', validators=[DataRequired()])
    m_name = StringField('Middle Name')
    l_name = StringField('Surname', validators=[DataRequired()])
    ext_name = StringField('Ext.')
    citizenship = StringField('Citizenship')
    gender = SelectField("Gender", choices=[('M', 'M'), ('F', 'F')])
    tup_id = StringField('TUP Student ID')
    college = SelectField("Assigned College", choices=[("COS", "College of Science"), ("CIE", "College of Industrial Education"), ("CIT", "College of Industrial Technology")], default='COS')
    email = StringField('Email')
    contact_no = StringField('Contact No.')
    residency = RadioField('Residency', choices=[('local', 'Local'), ('foreign', 'Foreign')])
    local_address = StringField('Local Address')
    foreign_address = StringField('International Address')
    birthyear = IntegerField('Year', validators = [DataRequired(), NumberRange(min=1950, max=datetime.now().year)])
    birthmonth = IntegerField('Month', validators = [DataRequired(), NumberRange(min=1, max=12)])
    birthday = IntegerField('Day', validators = [DataRequired(), NumberRange(min=1, max=31)])
    educational_backgrounds = FieldList(FormField(EducationalBackgroundForm))
    new_educational_background = FormField(EducationalBackgroundForm)
    civil_status = SelectField('Civil Status', choices=[("Single", "Single"), ("Married", "Married"), ("Legally Separated", "Legally Separated"), ("Widowed", "Widowed")])
    password = StringField('One-time Password')
    update = SubmitField('Update Account Details')
    submit = SubmitField('Add User')

    def __init__(self, data=None):
        super().__init__()
        if data:
            self.gender.default = data['gender']
            self.civil_status.default = data['civil_status']
            self.residency.default = data['residency']
            if 'college' in data.keys():
                self.college.default = data['college']
            self.process()
            
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8,message="Password must be at least 8 characters.")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Passwords do not match.")])
    submit = SubmitField('Save new password')

class FTLoginForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8,message="Password must be at least 8 characters.")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Passwords do not match.")])
    tup_id = StringField('TUP Student ID')
    f_name = StringField('First Name', validators=[DataRequired()])
    m_name = StringField('Middle Name')
    l_name = StringField('Surname', validators=[DataRequired()])
    ext_name = StringField('Ext.')
    citizenship = StringField('Citizenship', validators=[DataRequired()])
    gender = SelectField("Gender", choices=[('M', 'M'), ('F', 'F')])
    email = StringField('Email', validators=[DataRequired()])
    contact_no = StringField('Contact No.', validators=[DataRequired()])
    residency = RadioField('Residency', choices=[('local', 'Local'), ('foreign', 'Foreign')], default='local')
    local_address = StringField('Local Address', validators=[DataRequired()])
    foreign_address = StringField('International Address')
    birthyear = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1950, max=datetime.now().year)])
    birthmonth = IntegerField('Month', validators=[DataRequired(), NumberRange(min=1, max=12)])
    birthday = IntegerField('Day', validators=[DataRequired(), NumberRange(min=1, max=31)])
    civil_status = SelectField('Civil Status', choices=[("Single", "Single"), ("Married", "Married"), ("Legally Separated", "Legally Separated"), ("Widowed", "Widowed")], default="Single")
    submit = SubmitField('Save Account Details')

    def __init__(self, user_type):
        super().__init__()
        if user_type == 'student':
            self.tup_id.validators = [DataRequired()]

class ChangePasswordForm(FlaskForm):
    current = PasswordField('Current Password', validators=[DataRequired()])
    new = PasswordField('New Password', validators=[DataRequired(), Length(min=8,message="Password must be at least 8 characters.")])
    confirm = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new', "Passwords do not match.")])
    submit = SubmitField('Save New Password')

class ReceiptForm(FlaskForm):
    file = FileField('Upload OR and COR', validators=[DataRequired(), FileAllowed(['pdf', 'png', 'jpg'], 'Only .pdf, .png, and .jpg files allowed')])
    submit = SubmitField('Upload')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    code = StringField('Course Code', validators=[DataRequired()])
    submit = SubmitField('Add Course')

class RequirementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
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
    academic_year = StringField('Acad. Year', validators=[DataRequired("Academic year field cannot be empty.")])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired("Semester field cannot be empty.")])
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
        available_instructors = [(i['user'], f"{i['l_name'].capitalize()}, {i['f_name']} {i['m_name'][0]+'.' if i['m_name'] else ''}") for i in available_instructors]
        self.courses_select.choices += available_courses
        self.instructors_select.choices += available_instructors
        self.courses_select.validators = [DataRequired("Course selected is not a valid option.")]
        self.instructors_select.validators = [DataRequired("Select an instructor.")]

class StudentsFilterForm(FlaskForm):
    ay = SelectField('Academic Year', choices=[], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired()])
    submit = SubmitField('Apply')

    def __init__(self, academic_years):
        super().__init__()
        self.ay.choices = [(a, a) for a in academic_years]

class InstructorsFilterForm(FlaskForm):
    college = SelectField('College', choices=[("All", "All"), ("COS", "COS"), ("CIE", "CIE"), ("CIT", "CIT")])
    submit = SubmitField('Apply')

class DashboardStudentFilterForm(FlaskForm):
    ay = SelectField('Academic Year', choices=[("All", "All")], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[("All", "All"), ("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired()])
    college = SelectField('College', choices=[("All", "All"), ("COS", "COS"), ("CIE", "CIE"), ("CIT", "CIT")], validators=[DataRequired()])
    program = SelectField('Program', choices=[("All", "All")], validators=[DataRequired()])
    submit = SubmitField('Apply Filters')

    def __init__(self, options):
        super().__init__()
        self.ay.choices += [(a, a) for a in options['academic_years']]
        self.program.choices += [(a, a) for a in options['programs']]

class StudentReportFilterForm(FlaskForm):
    ay = SelectField('Academic Year', choices=[("All", "All")], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[("All", "All"), ("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired()])
    college = SelectField('College', choices=[("All", "All"), ("COS", "COS"), ("CIE", "CIE"), ("CIT", "CIT")], validators=[DataRequired()])
    program = SelectField('Program', choices=[("All", "All")], validators=[DataRequired()])
    age = BooleanField('Age')
    gender = BooleanField('Gender')
    residency = BooleanField('Residency')
    student_course_status = BooleanField('Course Status')

    def __init__(self, options):
        super().__init__()
        self.ay.choices += [(a, a) for a in options['academic_years']]
        self.program.choices += [(a, a) for a in options['programs']]

class FacultyReportFilterForm(FlaskForm):
    ay = SelectField('Academic Year', choices=[("All", "All")], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[("All", "All"), ("1st", "First"), ("2nd", "Second"), ("Midyear", "Midyear")], validators=[DataRequired()])
    college = SelectField('College', choices=[("All", "All"), ("COS", "COS"), ("CIE", "CIE"), ("CIT", "CIT")], validators=[DataRequired()])
    faculty_course_status = BooleanField('Course Status')
    honorarium = BooleanField('Status of Honorarium')

    def __init__(self, options):
        super().__init__()
        self.ay.choices += [(a, a) for a in options['academic_years']]