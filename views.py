from flask import Blueprint, request, redirect, url_for, session, render_template, g, jsonify, flash, send_from_directory
views = Blueprint('views', __name__)

from app import app
from forms import *
import db_functions as db

import os
from pathlib import Path

user_views = {
    'admin': [
        {'name': 'Overview', 'link': '.dashboard_admin'},
        {'name': 'Instructors', 'link': '.instructors'},
        {'name': 'Students', 'link': '.admin_students'},
        {'name': 'Courses', 'link': '.courses'},
        {'name': 'Message', 'link': '.message'},
        {'name': 'Manage Users', 'link': '.users'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
    'instructor': [
        {'name': 'Overview', 'link': '.dashboard_instructor'},
        {'name': 'Students', 'link': '.instructor_students'},
        {'name': 'Message', 'link': '.message'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
    'student': [
        {'name': 'Enrollment', 'link': '.enrollment'},
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
    student_count = db.get_student_count()
    return render_template('dashboard-admin.html', page="Dashboard", student_count=student_count, views=views)

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
        
@views.route('/admin_students')
def admin_students():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    students = db.get_students()
    return render_template('students-admin.html', page="Students", students=students, views=views)

@views.route('/instructor_students')
def instructor_students():
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('students-instructor.html', page="Students", views=views)

@views.route('/courses')
def courses():
    if g.user not in ['admin']:
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    courses = db.get_courses()
    return render_template('courses.html', page="Courses", courses=courses, views=views)

@views.route('/courses/add_course', methods=["GET", "POST"])
def add_course():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = CourseForm()
    if form.validate_on_submit():
        try:
            db.add_course(form.data)
            return f"""
            <script>
                window.opener.location.reload();
                window.close();
            </script>
            """
        except Exception as e:
            return jsonify({"message": f"Problem adding course"}), 400
    return render_template('add_course.html', form=form)

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
    instructors = db.get_users('instructor')
    students = db.get_users('student')
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
            db.add_user(form.data)
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
    student = db.get_student(session.get('id'))
    receipt_form = ReceiptForm()
    document_form = DocumentForm()
    receipt_fp = url_for('.get_receipt', user_id=session.get('id'))
    document_fp = url_for('.get_document', user_id=session.get('id'))
    return render_template('enrollment.html', page="Enrollment", student=student, receipt_form=receipt_form, receipt_fp=receipt_fp, document_fp=document_fp, document_form=document_form, views=views)
    
@views.route('/receipt', methods=['POST'])
def receipt():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    form = ReceiptForm()
    if form.validate_on_submit():
        try:
            db.upload_receipt(session.get("id"), form.file)
            flash('Receipt uploaded successfully.')
        except Exception as e:
            flash(f'Problem uploading document. {e}', 'error')
    else:
        flash(f"Problem uploading document. {'. '.join(form.file.errors)}", 'error')
    return redirect(url_for('.enrollment'))

@views.route('/document', methods=['POST'])
def document():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    form = DocumentForm()
    if form.validate_on_submit():
        try:
            db.upload_document(session.get("id"), form.file)
            flash('Document uploaded successfully.')
        except Exception as e:
            flash(f'Problem uploading document. {e}', 'error')
    else:
        flash(f"Problem uploading document. {'. '.join(form.file.errors)}", 'error')
    return redirect(url_for('.enrollment'))
    
@views.route('/uploads/receipts/<user_id>')
def get_receipt(user_id):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'receipts'), 'receipt_' + str(user_id) + '.jpg')

@views.route('/uploads/documents/<user_id>')
def get_document(user_id):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), 'document_' + str(user_id) + '.pdf')

@views.route('/students/<user_id>/approve/<progress>', methods=['GET', 'POST'])
def approve_document(user_id, progress):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = StatusConfirmationForm()
    receipt_fp = url_for('.get_receipt', user_id=user_id)
    document_fp = url_for('.get_document', user_id=user_id)
    if form.validate_on_submit():
        message = db.move_student_progress(user_id, progress)
        return f"""
        <script>
            alert("{message}");
            window.opener.location.reload();
            window.close();
        </script>
        """
    return render_template('approve-status.html', form=form, user_id=user_id, progress=progress, receipt_fp=receipt_fp, document_fp=document_fp)

@views.route('/students/<user_id>/courses', methods=['GET', 'POST'])
def enroll_student(user_id):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    data = db.get_student_enrollment_options(user_id)
    form = StudentCoursesForm(data['available_courses'], data['instructors'])
    if form.validate_on_submit():
        message = db.enroll_student(user_id, form.data)
        data = db.get_student_enrollment_options(user_id)
        flash(f"{message}")
    else:
        if form.courses_select.errors:
            flash(f"{form.courses_select.errors[0]}", 'error')
        if form.instructors_select.errors:
            flash(f"{form.instructors_select.errors[0]}", 'error')
    return render_template('modify-courses.html', form=form, data=data)

@views.route('/account')
def account():
    views = user_views[g.user]
    return render_template('account.html', page="Account", views=views)

@views.route('/unauthorized')
def unauthorized():
    return 'Unauthorized to access to this resource.'