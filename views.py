from flask import Blueprint, request, redirect, url_for, session, render_template, g, jsonify, flash, send_from_directory
views = Blueprint('views', __name__)

from app import app
from forms import *
import db_functions as db

import os
from pathlib import Path
from datetime import datetime

user_views = {
    'admin': [
        {'name': 'Overview', 'link': '.dashboard_admin'},
        {'name': 'Instructors', 'link': '.instructors'},
        {'name': 'Students', 'link': '.admin_students'},
        {'name': 'Courses', 'link': '.courses'},
        {'name': 'Manage Users', 'link': '.users'},
        {'name': 'Manage Account', 'link': '.account'},
        {'name': 'System Settings', 'link': '.system'},
        {'name': 'Generate Report', 'link': '.report'},
    ],
    'instructor': [
        {'name': 'Students', 'link': '.instructor_students'},
        {'name': 'Manage Account', 'link': '.account'},
    ],
    'student': [
        {'name': 'Enrollment', 'link': '.enrollment'},
        {'name': 'Subjects', 'link': '.subjects'},
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
    user = db.get_user(session.get('id'))
    if user['ft_login']:
        return redirect('/login')
    views = user_views[g.user]
    return redirect(url_for(views[0]['link']))

@views.route('/system', methods=['GET', 'POST'])
def system():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    form = SystemForm()
    if form.validate_on_submit():
        success, message = db.update_system_settings(form.data)
        if success:
            flash(message, 'message')
        else:
            flash(message, 'error')
    if form.academic_year.errors:
        for error in form.academic_year.errors:
            flash(error, 'error')
    data = db.get_system_settings()
    return render_template('system.html', page="System Settings", form=form, data=data, views=views)

@views.route('/report', methods=['GET', 'POST'])
def report():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    options = {
        'academic_years': db.get_academic_years(),
        'programs': [p['abbr'] for p in db.get_programs()]
    }
    student_report_form = StudentReportFilterForm(options=options)
    faculty_report_form = FacultyReportFilterForm(options=options)
    return render_template('report-filters.html', views=views, page="Generate Report", student_report_form=student_report_form, faculty_report_form=faculty_report_form)

@views.route('/student_report', methods=['POST'])
def student_report():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    options = {
        'academic_years': db.get_academic_years(),
        'programs': [p['abbr'] for p in db.get_programs()]
    }
    student_report_form = StudentReportFilterForm(options=options)
    if student_report_form.validate_on_submit():
        data = db.generate_student_report(student_report_form.data)
        param = student_report_form.data
        filename = f"Student Report - {param['ay']} - {param['semester']} Semester - {'All Colleges' if param['college'] == 'All' else param['college']} - {'All Programs' if param['program'] == 'All' else param['program']}"
        success, message = db.create_student_excel(filename, data)
        if success:
            return(send_from_directory('.', f'{filename}.xlsx'))
        return f"""
            <script>
                alert("{message}");
            </script>
            """
    return redirect(url_for('.report'))

@views.route('/faculty_report', methods=['POST'])
def faculty_report():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    options = {
        'academic_years': db.get_academic_years(),
        'programs': [p['abbr'] for p in db.get_programs()]
    }
    faculty_report_form = FacultyReportFilterForm(options=options)
    if faculty_report_form.validate_on_submit():
        data = db.generate_faculty_report(faculty_report_form.data)
        param = faculty_report_form.data
        filename = f"Faculty Report - {param['ay']} - {param['semester']} Semester - {'All Colleges' if param['college'] == 'All' else param['college']}"
        success, message = db.create_faculty_excel(filename, data)
        if success:
            return(send_from_directory('.', f'{filename}.xlsx'))
        return f"""
            <script>
                alert("{message}");
            </script>
            """
    return redirect(url_for('.report'))

@views.route('/admin_dashboard', methods=['GET', 'POST'])
def dashboard_admin():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    options = {
        'academic_years': db.get_academic_years(),
        'programs': [p['abbr'] for p in db.get_programs()]
    }
    student_filter_form = DashboardStudentFilterForm(options)
    if student_filter_form.validate_on_submit():
        filter = student_filter_form.data
    else:
        filter = {
            'ay': 'All',
            'semester': 'All',
            'college': 'All',
            'program': 'All'
        }
    student_report_filters = {
        'ay': filter['ay'],
        'semester': filter['semester'],
        'college': filter['college'],
        'program': filter['program'],
        'age': True,
        'gender': True,
        'residency': True,
        'student_course_status': True
    }
    student_data = db.generate_student_report(student_report_filters)
    graphs = {
        'age': {'labels': [], 'data': [], 'type': 'bar', 'title': "Age Chart", 'x_label': "Age"},
        'gender': {'labels': [], 'data': [], 'type': 'pie', 'title': "Gender Chart", 'x_label': ""},
        'residency': {'labels': [], 'data': [], 'type': 'pie', 'title': "Residency Chart", 'x_label': ""},
        'course_status': {'labels': [], 'data': [], 'type': 'bar', 'title': "Course Status Chart", 'x_label': "Course Status"},
    }

    for key in graphs.keys():
        for label, data in student_data[key].items():
            graphs[key]['labels'].append(label)
            graphs[key]['data'].append(data) 

    return render_template('dashboard-admin.html', page="Dashboard", views=views, s_form=student_filter_form, graphs=graphs)

@views.route('/instructor_dashboard')
def dashboard_instructor():
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    return render_template('dashboard-instructor.html', page="Dashboard", views=views)

@views.route('/instructors', methods=['GET', 'POST'])
def instructors():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    instructors = db.get_instructors()
    form = InstructorsFilterForm()
    data = { 'instructors': [] }
    if form.validate_on_submit():
        filter = form.data
    else:
        filter = {'college': "All"}
    for i in instructors:
        if filter['college'] != "All" and filter['college'] != i['college']:
            continue
        info = {
            'name': f"{i['l_name'].title()}, {i['f_name']} {i['m_name'][0]+'.' if i['m_name'] else ''}",
            'username': i['username'],
            'id': i['id'],
            'uid': i['user'],
            'college': i['college']
        }
        data['instructors'].append(info)
    data['instructors'].sort(key=lambda x: x['college'])
    return render_template('instructors.html', page="Instructors", data=data, form=form, views=views)

@views.route('/admin_students', methods=["GET", "POST"])
def admin_students():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    students = db.get_students()
    data = { 'students': [] }
    form = StudentsFilterForm(db.get_academic_years())
    for s in students:
        info = {
            'name': f"{s['l_name'].title()}, {s['f_name']} {s['m_name'][0]+'.' if s['m_name'] else ''}",
            'username': s['username'],
            'id': s['id'],
            'uid': s['user'],
            'tup_id': s['tup_id'],
            'program': db.get_program(s['program'])['abbr'],
            'progress': s['progress'],
            'receipt': s['receipt_filepath'],
            'ay': s['ay'],
            'semester': s['semester']
        }
        data['students'].append(info)
    if form.validate_on_submit():
        filter = form.data
    else:
        cfg = db.get_system_settings()
        form.ay.data = str(cfg['academic_year'])
        form.semester.data = str(cfg['semester'])
        filter = form.data
    data['students'] = [s for s in data['students'] if str(s['ay']) == filter['ay'] and str(s['semester']) == filter['semester']]
    return render_template('students-admin.html', page="Students", data=data, form=form, views=views)

@views.route('/users/<user_id>/profile')
def profile(user_id):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    data = db.get_account_details(user_id)
    return render_template('profile.html', page="Profile", data=data, views=views)

@views.route('/instructor_students', methods=["GET", "POST"])
def instructor_students():
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    enrollments = db.get_instructor_enrollments(db.uid_to_pk(session.get('id'), 'instructor'))
    data = {
        'instructor_id': db.uid_to_pk(session.get('id'), 'instructor'),
        'enrollments': []
    }
    form = StudentsFilterForm(db.get_academic_years())
    for e in enrollments:
        data['enrollments'].append({
            'student_name': f"{e['student']['l_name'].title()}, {e['student']['f_name']} {e['student']['m_name'][0]+'.' if e['student']['m_name'] else ''}",
            'course': f"{e['course']['code']}: {e['course']['title']}",
            'status': e['status'],
            'enrollment_id': e['id'],
            'grade': e['grade'],
            'ay': e['ay'],
            'semester': e['semester'],
            'honorarium': e['honorarium']
        })
    if form.validate_on_submit():
        filter = form.data
    else:
        cfg = db.get_system_settings()
        form.ay.data = str(cfg['academic_year'])
        form.semester.data = str(cfg['semester'])
        filter = form.data
    data['enrollments'] = [e for e in data['enrollments'] if str(e['ay']) == filter['ay'] and str(e['semester']) == filter['semester']]
    return render_template('students-instructor.html', page="Students", form=form, data=data, views=views)

@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/accept', methods=["GET", "POST"])
def accept_enrollment(instructor_id, enrollment_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    form = StatusConfirmationForm()
    e = db.get_instructor_enrollment(instructor_id, enrollment_id)
    data = {
        'student_name': f"{e['student']['l_name'].title()}, {e['student']['f_name']} {e['student']['m_name'][0] if e['student']['m_name'] else ''}.",
        'course': f"{e['course']['code']}: {e['course']['title']}",
        'instructor_id': instructor_id,
        'enrollment_id': enrollment_id
    }
    if form.validate_on_submit():
        message = db.accept_enrollment(enrollment_id)
        return f"""
        <script>
            alert("{message}");
            window.opener.location.reload();
            window.close();
        </script>
        """
    return render_template('accept-enrollment.html', data=data, form=form)

@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/requirements', methods=["GET", "POST"])
def view_instructor_requirements(instructor_id, enrollment_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    data = db.get_requirements(enrollment_id)
    enrollment = db.get_enrollment(enrollment_id)
    course = db.get_course(enrollment['course'])
    course = f"{course['code']}: {course['title']}"
    return render_template('requirements-instructor.html', data=data, course=course, instructor_id=instructor_id, enrollment_id=enrollment_id)

@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/requirements/<requirement_id>', methods=["GET", "POST"])
def view_instructor_requirement(instructor_id, enrollment_id, requirement_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    data = db.get_requirement(requirement_id)
    enrollment = db.get_enrollment(enrollment_id)
    course = db.get_course(enrollment['course'])
    course = f"{course['code']}: {course['title']}"
    return render_template('requirement-instructor.html', data=data, course=course, instructor_id=instructor_id, enrollment_id=enrollment_id, requirement_id=requirement_id)

@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/submit_grade', methods=["GET", "POST"])
def submit_grade(instructor_id, enrollment_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    e = db.get_instructor_enrollment(instructor_id, enrollment_id)
    data = {
        'name': f"{e['student']['l_name'].capitalize()} {e['student']['f_name']} {e['student']['m_name'] if e['student']['m_name'] else ''}",
        'course': e['course']['code']
    }
    form = GradeSubmissionForm()
    if form.validate_on_submit():
        success, message = db.submit_grade(enrollment_id, form.data)
        if success:
            return f"""
            <script>
                alert("{message}");
                window.opener.location.reload();
                window.close();
            </script>
            """
        else:
            return f"""
            <script>
                alert("{message}");
            </script>
            """
    return render_template('submit-grade.html', data=data, form=form, instructor_id=instructor_id, enrollment_id=enrollment_id)

@views.route('/students/<student_id>/enrollments/<enrollment_id>/requirements', methods=["GET", "POST"])
def view_student_requirements(student_id, enrollment_id):
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    data = db.get_requirements(enrollment_id)
    enrollment = db.get_enrollment(enrollment_id)
    course = db.get_course(enrollment['course'])
    course = f"{course['code']}: {course['title']}"
    return render_template('requirements-student.html', data=data, course=course, student_id=student_id, enrollment_id=enrollment_id)

@views.route('/students/<student_id>/enrollments/<enrollment_id>/requirements/<requirement_id>', methods=["GET", "POST"])
def view_student_requirement(student_id, enrollment_id, requirement_id):
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    form = SubmissionForm()
    data = db.get_requirement(requirement_id)
    enrollment = db.get_enrollment(enrollment_id)
    course = db.get_course(enrollment['course'])
    course = f"{course['code']}: {course['title']}"
    if form.validate_on_submit():
        try:
            message = db.add_submission(requirement_id, form)
        except Exception as e:
            return jsonify({"message": f"{e}"}), 400
    return render_template('requirement-student.html', data=data, form=form, course=course, student_id=student_id, enrollment_id=enrollment_id, requirement_id=requirement_id)

@views.route('/students/<student_id>/enrollments/<enrollment_id>/requirements/<requirement_id>/turn_in')
def turn_in_submission(student_id, enrollment_id, requirement_id):
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    try:
        message = db.turn_in_submission(requirement_id)
        return redirect(url_for('.view_student_requirement', student_id=student_id, enrollment_id=enrollment_id, requirement_id=requirement_id))
    except Exception as e:
        return jsonify({"message": f"{e}"}), 400
    
@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/requirements/<requirement_id>/return')
def return_submission(instructor_id, enrollment_id, requirement_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    try:
        message = db.return_submission(requirement_id)
        return redirect(url_for('.view_instructor_requirement', instructor_id=instructor_id, enrollment_id=enrollment_id, requirement_id=requirement_id))
    except Exception as e:
        return jsonify({"message": f"{e}"}), 400

@views.route('/instructors/<instructor_id>/enrollments/<enrollment_id>/requirements/add', methods=["GET", "POST"])
def add_requirement(instructor_id, enrollment_id):
    if g.user != 'instructor':
        return redirect(url_for('.unauthorized'))
    form = RequirementForm()
    if form.validate_on_submit():
        try:
            message = db.add_requirement(enrollment_id, form)
            return redirect(url_for('.view_instructor_requirements', instructor_id=instructor_id, enrollment_id=enrollment_id))
        except Exception as e:
            return jsonify({"message": f"{e}"}), 400
    return render_template('add_requirement.html', instructor_id=instructor_id, enrollment_id=enrollment_id, form=form)

@views.route('/courses')
def courses():
    if g.user not in ['admin']:
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    colleges = db.get_programs_by_college()
    courses = db.get_courses()
    return render_template('courses.html', page="Courses", colleges=colleges, courses=courses, views=views)

@views.route('/courses/add_course', methods=["GET", "POST"])
def add_course():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = CourseForm()
    if form.validate_on_submit():
        success, message = db.add_course(form.data)
        if success:
            flash(message, 'info')
        else:
            flash(message, 'error')
        return redirect(url_for('.courses'))
    return render_template('add_course.html', form=form)

@views.route('/subjects')
def subjects():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    data = db.get_student_enrollments(db.uid_to_pk(session.get('id'), 'student'))
    student_id = db.uid_to_pk(session.get('id'), 'student')
    for i in data:
        i['instructor']['name'] = f"{i['instructor']['l_name'].title()}, {i['instructor']['f_name']} {i['instructor']['m_name'][0]+'.' if i['instructor']['m_name'] else ''}"
    return render_template('subjects.html', page="Subjects", data=data, student_id=student_id, views=views)

@views.route('/message')
def message():
    views = user_views[g.user]
    return render_template('message.html', page="Message", views=views)

@views.route('/users')
def users():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    instructors = db.get_instructors()
    students = db.get_students()
    return render_template('users.html', page="Users", instructors=instructors, students=students, views=views)

@views.route('/users/add_user/<user_type>', methods=["GET", "POST"])
def add_user(user_type):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = NewAccountForm()
    form.user_type.data = user_type
    if form.validate_on_submit():
        success, message = db.add_user(form.data)
        if success:
            flash(message, 'info')
        else:
            flash(message, 'error')
        return redirect(url_for('.users'))
    if form.errors:
        return redirect(url_for('.users'))
    return jsonify({'html': render_template('add_user.html', user_type=user_type, form=form)}), 200

@views.route('/users/<id>/reset_password')
def reset_password(id):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    success, message = db.reset_password(id)
    return jsonify({"message": message}), 200 if success else 300

@views.route('/enrollment')
def enrollment():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    views = user_views[g.user]
    student = db.get_student(session.get('id'))
    receipt_form = ReceiptForm()
    receipt_fp = url_for('.get_receipt', user_id=session.get('id'))
    return render_template('enrollment.html', page="Enrollment", student=student, receipt_form=receipt_form, receipt_fp=receipt_fp, views=views)
    
@views.route('/receipt', methods=['POST'])
def receipt():
    if g.user != 'student':
        return redirect(url_for('.unauthorized'))
    form = ReceiptForm()
    if form.validate_on_submit():
        try:
            db.upload_receipt(session.get("id"), form.data)
            flash('Receipt uploaded successfully.')
        except Exception as e:
            flash(f'Problem uploading document. {e}', 'error')
    else:
        flash(f"Problem uploading document. {'. '.join(form.file.errors)}", 'error')
    return redirect(url_for('.enrollment'))
    
@views.route('/uploads/receipts/<user_id>')
def get_receipt(user_id):
    fp = db.get_receipt_fp(user_id)
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'receipts'), fp)

@views.route('/uploads/forms/grade_submission_form1')
def get_grade_submission_form1():
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'forms'), "Daily Time Record 3.docx")

@views.route('/uploads/forms/grade_submission_form2')
def get_grade_submission_form2():
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'forms'), "Student's Summary Grade Report 4.docx")

@views.route('/uploads/forms/grade_submission_form3')
def get_grade_submission_form3():
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'forms'), "TER.Tutor's Evaluation Report  2.docx")

@views.route('/uploads/<path:fp>')
def ref_fp(fp):
    path = os.path.split(fp)
    directory = '/'.join(path[:-1])
    filename = path[-1]
    return send_from_directory(directory, filename)

@views.route('/uploads/grade_forms/<form>/<enrollment>')
def grade_forms(form, enrollment):
    enrollment = db.get_enrollment(enrollment)
    fp = enrollment[f'form{form}']
    directory = os.path.join(app.config['UPLOAD_FOLDER'], 'grades')
    return send_from_directory(directory, fp)

@views.route('/release_honorarium', methods=['POST'])
def release_honorarium():
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    enrollment_id = request.get_json()['enrollment_id']
    success, message = db.release_honorarium(enrollment_id)
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': message}), 400

@views.route('/students/<student_id>/approve/<progress>', methods=['GET', 'POST'])
def approve_document(student_id, progress):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    form = StatusConfirmationForm()
    receipt_fp = url_for('.get_receipt', user_id=db.pk_to_uid(student_id, 'student'))
    if form.validate_on_submit():
        success, message = db.move_student_progress(student_id, progress)
        return redirect(url_for('.admin_students'))
    return render_template('approve-status.html', form=form, student_id=student_id, progress=progress, receipt_fp=receipt_fp)

@views.route('/students/<student_id>/courses', methods=['GET', 'POST'])
def enroll_student(student_id):
    if g.user != 'admin':
        return redirect(url_for('.unauthorized'))
    data = db.get_student_enrollment_options(student_id)
    data['student']['name'] = f"{data['student']['l_name'].title()}, {data['student']['f_name']} {data['student']['m_name'][0]+'.' if data['student']['m_name'] else ''}"
    data['student']['program'] = db.get_program(data['student']['program'])['abbr']
    programs_form = StudentProgramForm(data['programs'])
    courses_form = StudentCoursesForm(data['available_courses'], data['instructors'])
    if data['student']['ay']:
        programs_form.academic_year.data = data['student']['ay']
    else:
        programs_form.academic_year.data = datetime.now().year
    programs_form.semester.data = data['student']['semester']
    programs_form.programs_select.data = data['student']['program']   
    return render_template('modify-courses.html', programs_form=programs_form, courses_form=courses_form, data=data)

@views.route('/students/<student_id>/enroll/program', methods=['POST'])
def enroll_student_in_program(student_id):
    data = db.get_student_enrollment_options(student_id)
    programs_form = StudentProgramForm(data['programs'])
    if programs_form.validate_on_submit():
        message = db.enroll_student_in_program(student_id, programs_form.data)
    # else:
    #     if programs_form.academic_year.errors:
    #         flash(f"{programs_form.academic_year.errors[0]}", 'error')
    #     if programs_form.semester.errors:
    #         flash(f"{programs_form.semester.errors[0]}", 'error')
    #     if programs_form.academic_year.errors:
    #         flash(f"{programs_form.programs_select.errors[0]}", 'error')
    return redirect(url_for('.admin_students'))

@views.route('/students/<student_id>/enroll/course', methods=['POST'])
def enroll_student_in_course(student_id):
    data = db.get_student_enrollment_options(student_id)
    courses_form = StudentCoursesForm(data['available_courses'], data['instructors'])
    if courses_form.validate_on_submit():
        message = db.enroll_student_in_course(student_id, courses_form.data)
    return redirect(url_for('.admin_students'))

@views.route('/account', methods=['GET', 'POST'])
def account():
    views = user_views[g.user]
    data = db.get_account_details(session.get('id'))
    account_form = UserAccountForm(data=data)
    pass_form = ChangePasswordForm()
    if session.get('user') == 'instructor':
        educational_backgrounds = db.get_educational_background(session.get('id'))
        for e in educational_backgrounds:
            e_form = EducationalBackgroundForm()
            e_form.id.data = e['id']
            e_form.school.data = e['school']
            e_form.degree.data = e['degree']
            e_form.start_year.data = e['start_year']
            e_form.end_year.data = e['end_year']
            e_form.academic_honors.data = e['academic_honors']
            account_form.educational_backgrounds.append_entry(e_form.data)
    user_type = session.get('user')
    return render_template('account.html', page="Account", account_form=account_form, pass_form=pass_form, data=data, user_type=user_type, views=views)

@views.route('/account/change_account_details', methods=['POST'])
def change_account_details():
    form = UserAccountForm()
    if request.method == "POST":
        if "Update" in request.form.values():
            for eb_form in form.educational_backgrounds:
                db.update_educational_background(eb_form.data)
            return redirect(url_for('.account'))
        if "Add" in request.form.values():
            db.add_educational_background(session.get('id'), form.new_educational_background.data)
            return redirect(url_for('.account'))
        success, message = db.update_account_details(session.get('id'), form.data)
        if success:
            flash(f"{message}", 'message')
        else:
            flash(f"{message}", 'error')
    if form.errors:
        flash(f"{form.errors}", 'error')
    return redirect(url_for('.account'))

@views.route('/account/change_password', methods=['POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        success, message = db.change_password(session.get('id'), form.data)
        if success:
            flash(f"{message}", 'message')
        else:
            flash(f"{message}", 'error')
    if form.errors:
        flash(f"{form.errors}", 'error')
    return redirect(url_for('.account'))

@views.route('/unauthorized')
def unauthorized():
    return 'Unauthorized to access to this resource.'