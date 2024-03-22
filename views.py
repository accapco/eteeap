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

class FileForm(FlaskForm):
    file = FileField('Upload PDF File', validators=[validators.DataRequired(), FileAllowed(['pdf'], 'Only PDF files allowed')])
    submit = SubmitField('Upload')

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    code = StringField('Course Code', validators=[validators.DataRequired()])
    submit = SubmitField('Add Course')

from app import db
from models import *

def _get_users(user_type):
    return [u.__dict__ for u in User.query.filter_by(user_type=user_type).all()]

def _add_user(user):
    new_user = User(
        username=user['username'], 
        f_name=user['f_name'],
        m_name=user['m_name'],
        l_name=user['l_name'],
        password=user['password'],
        user_type=user['user_type']
    )
    db.session.add(new_user)
    db.session.commit()
    if user['user_type'] == "admin":
        new_admin = Admin(user_id=new_user.id)
        db.session.add(new_admin)
    elif user['user_type'] == "instructor":
        new_instructor = Instructor(user_id=new_user.id)
        db.session.add(new_instructor)
    else:
        new_student = Student(user_id=new_user.id)
        db.session.add(new_student)
    db.session.commit()

def _get_courses():
    return [u.__dict__ for u in Course.query.all()]

def _add_course(course):
    new_course = Course(
        title = course['title'],
        code = course['code']
    )
    db.session.add(new_course)
    db.session.commit()

def _get_student(user_id):
    return Student.query.filter_by(user_id=user_id).first().__dict__

def _get_documents(user_id):
    return [u.__dict__ for u in Document.query.filter_by(user_id=user_id).all()]

def _add_document(upload):
    new_document = Document(user_id=session.get('id'), file=upload.read(), filename=upload.filename)
    db.session.add(new_document)
    db.session.commit()

from flask import Blueprint, request, redirect, url_for, session, render_template, g, jsonify
views = Blueprint('views', __name__)

user_views = {
    'admin': [
        {'name': 'Overview', 'link': '.dashboard_admin'},
        {'name': 'Instructors', 'link': '.instructors'},
        {'name': 'Students', 'link': '.students'},
        {'name': 'Courses', 'link': '.courses'},
        {'name': 'Message', 'link': '.message'},
        {'name': 'Manage Users', 'link': '.users'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
    'instructor': [
        {'name': 'Overview', 'link': '.dashboard_instructor'},
        {'name': 'Students', 'link': '.students'},
        {'name': 'Message', 'link': '.message'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
    'student': [
        {'name': 'Enrollment', 'link': '.enrollment'},
        {'name': 'Documents', 'link': '.documents'},
        {'name': 'Subjects', 'link': '.subjects'},
        {'name': 'Message', 'link': '.message'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
}

@views.before_request
def verify_permissions():
    g.user = None
    if 'user' in session:
        g.user = session['user']
    else:
        return redirect('/login')

@views.route('/home')
def index():
    views = user_views[g.user]
    return redirect(url_for(views[0]['link']))

@views.route('/admin_dashboard')
def dashboard_admin():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('dashboard-admin.html', page="Dashboard", views=views)

@views.route('/instructor_dashboard')
def dashboard_instructor():
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('dashboard-instructor.html', page="Dashboard", views=views)

@views.route('/instructors')
def instructors():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('instructors.html', page="Instructors", views=views)
        
@views.route('/students')
def students():
    if g.user not in ['admin', 'instructor']:
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('students.html', page="Students", views=views)

@views.route('/courses')
def courses():
    if g.user not in ['admin']:
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    courses = _get_courses()
    return render_template('courses.html', page="Courses", courses=courses, views=views)

@views.route('/courses/add_course', methods=["GET", "POST"])
def add_course():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = CourseForm()
    if form.validate_on_submit():
        try:
            _add_course(form.data)
            return f"""
            <script>
                window.opener.location.reload();
                window.close();
            </script>
            """
        except Exception as e:
            return jsonify({"message": f"Problem adding course"}), 400
    return render_template('add_course.html', form=form)

@views.route('/documents', methods=['GET', 'POST'])
def documents():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    form = FileForm()
    if form.validate_on_submit():
        try:
            _add_document(form.file.data)
            return f"Uploaded document {form.file.data.filename}"
        except Exception as e:
            return jsonify({"message": f"Problem uploading document. {e}"}), 400
    views = user_views[g.user]
    documents = _get_documents(session.get("id"))
    return render_template('documents.html', page="Documents", documents=documents, form=form, views=views)

@views.route('/subjects')
def subjects():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('subjects.html', page="Subjects", views=views)

@views.route('/message')
def message():
    views = user_views[g.user]
    return render_template('message.html', page="Message", views=views)

@views.route('/users')
def users():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    instructors = _get_users('instructor')
    students = _get_users('student')
    return render_template('users.html', page="Users", instructors=instructors, students=students, views=views)

@views.route('/users/add_user/<user_type>', methods=["GET", "POST"])
def add_user(user_type):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = UserForm()
    if request.method == 'POST':
        form.user_type.data = user_type
    if form.validate_on_submit():
        try:
            _add_user(form.data)
            return f"""
            <script>
                window.opener.location.reload();
                window.close();
            </script>
            """
        except Exception as e:
            return jsonify({"message": f"Problem adding {user_type} account"}), 400
    return render_template('add_user.html', user_type=user_type, form=form)

@views.route('/enrollment')
def enrollment():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    student = _get_student(session.get("id"))
    return render_template('enrollment.html', page="Enrollment", student=student, views=views)
    
@views.route('/account')
def account():
    views = user_views[g.user]
    return render_template('account.html', page="Account", views=views)

@views.route('/unauthorized')
def unauthorized():
    return 'Unauthorized to access to this resource.'