from app import app, db
from models import *
from sqlalchemy import func
from uuid import uuid4
import os
import sys

def get_user(user_id):
    return User.query.filter_by(id=user_id).first().__dict__

def get_users(user_type):
    return [u.__dict__ for u in User.query.filter_by(user_type=user_type).all()]

def uid_to_pk(uid, user_type):
    if user_type == 'student':
        obj = Student
    elif user_type == 'instructor':
        obj = Instructor
    elif user_type == 'admin':
        obj = Admin
    else:
        return "Error"
    return obj.query.filter_by(user=uid).first().__dict__['id']

def pk_to_uid(id, user_type):
    if user_type == 'student':
        obj = Student
    elif user_type == 'instructor':
        obj = Instructor
    elif user_type == 'admin':
        obj = Admin
    else:
        return "Error"
    return obj.query.filter_by(id=id).first().__dict__['user']

def add_user(user):
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
        new_admin = Admin(user=new_user.id)
        db.session.add(new_admin)
    elif user['user_type'] == "instructor":
        new_instructor = Instructor(user=new_user.id)
        db.session.add(new_instructor)
    else:
        new_student = Student(user=new_user.id)
        db.session.add(new_student)
    db.session.commit()

def get_instructor(user_id):
    instructor = Instructor.query.filter_by(user=user_id).first().__dict__
    userinfo = get_user(instructor['user'])
    instructor['f_name'] = userinfo['f_name']
    instructor['l_name'] = userinfo['l_name']
    instructor['m_name'] = userinfo['m_name']
    instructor['username'] = userinfo['username']
    return instructor

def get_instructor_bypk(id):
    instructor = Instructor.query.filter_by(id=id).first().__dict__
    userinfo = get_user(instructor['user'])
    instructor['f_name'] = userinfo['f_name']
    instructor['l_name'] = userinfo['l_name']
    instructor['m_name'] = userinfo['m_name']
    instructor['username'] = userinfo['username']
    return instructor

def get_instructors():
    instructors = []
    for instructor in Instructor.query.all():
        instructor = instructor.__dict__
        userinfo = get_user(instructor['user'])
        instructor['f_name'] = userinfo['f_name']
        instructor['l_name'] = userinfo['l_name']
        instructor['m_name'] = userinfo['m_name']
        instructor['username'] = userinfo['username']
        instructors.append(instructor)
    return instructors

def get_instructor_enrollments(instructor_id):
    enrollments = Enrollment.query.filter_by(instructor=instructor_id).all()
    response = []
    for e in enrollments:
        e = e.__dict__
        e['student'] = get_student_bypk(e['student'])
        e['course'] = get_course(e['course'])
        response.append(e)
    return response

def get_instructor_enrollment(instructor_id, enrollment_id):
    response = Enrollment.query.filter_by(instructor=instructor_id, id=enrollment_id).first().__dict__
    response['student'] = get_student_bypk(response['student'])
    response['course'] = get_course(response['course'])
    return response

def accept_enrollment(enrollment_id):
    enrollment = Enrollment.query.filter_by(id=enrollment_id).first()
    if enrollment.status == 'pending':
        enrollment.status = 'ongoing'
        db.session.commit()
        return "Enrollment accepted."
    else:
        return "Invalid operation"

def get_requirements(enrollment_id):
    requirements = Requirement.query.filter_by(enrollment=enrollment_id).all()
    response = []
    for r in requirements:
        r = r.__dict__
        r['description'] = r['description'].split('\n')
        r['materials'] = get_materials(r['id'])
        r['submissions'] = get_submissions(r['id'])
        response.append(r)
    return response

def get_requirement(requirement_id):
    return Requirement.query.filter_by(id=requirement_id).first().__dict__

def add_requirement(enrollment_id, form):
    enrollment = Enrollment.query.filter_by(id=enrollment_id).first()
    new_requirement = Requirement(
        enrollment = enrollment.id,
        title = form.title.data,
        description = form.description.data,
        progress = 'incomplete'
    )
    try:
        db.session.add(new_requirement)
        db.session.commit()
        for file in form.materials.data:
            print(f'{file.filename}', file=sys.stdout)
            filename = str(uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'materials', filename)
            file.save(filepath)
            new_material = RequirementMaterial(filepath=filepath, requirement=new_requirement.id)
            db.session.add(new_material)
        db.session.commit()
        return "Requirement posted."
    except Exception as e:
        db.session.rollback()
        return f"An error occured while posting the requirement: {e}"

def get_materials(requirement_id):
    materials = RequirementMaterial.query.filter_by(requirement=requirement_id).all()
    response = []
    for m in materials:
        response.append(m.__dict__)
    return response

def get_submissions(requirement_id):
    submissions = RequirementSubmission.query.filter_by(requirement=requirement_id).all()
    response = []
    for s in submissions:
        response.append(s.__dict__)
    return response

def get_student(user_id):
    student = Student.query.filter_by(user=user_id).first().__dict__
    userinfo = get_user(student['user'])
    student['f_name'] = userinfo['f_name']
    student['l_name'] = userinfo['l_name']
    student['m_name'] = userinfo['m_name']
    student['username'] = userinfo['username']
    return student

def get_student_bypk(id):
    student = Student.query.filter_by(id=id).first().__dict__
    userinfo = get_user(student['user'])
    student['f_name'] = userinfo['f_name']
    student['l_name'] = userinfo['l_name']
    student['m_name'] = userinfo['m_name']
    student['username'] = userinfo['username']
    return student

def get_students():
    students = []
    for student in Student.query.all():
        student = student.__dict__
        userinfo = get_user(student['user'])
        student['f_name'] = userinfo['f_name']
        student['l_name'] = userinfo['l_name']
        student['m_name'] = userinfo['m_name']
        student['username'] = userinfo['username']
        students.append(student)
    return students

def get_student_count():
    payment_count = db.session.query(func.count(Student.id)).filter(Student.progress == 'payment').scalar()
    evaluation_count = db.session.query(func.count(Student.id)).filter(Student.progress == 'evaluation').scalar()
    enrollment_count = db.session.query(func.count(Student.id)).filter(Student.progress == 'enrollment').scalar()
    completion_count = db.session.query(func.count(Student.id)).filter(Student.progress == 'completion').scalar()
    return {
        'payment': payment_count,
        'evaluation': evaluation_count,
        'enrollment': enrollment_count,
        'completion': completion_count
    }

def get_student_enrollments(student_id):
    enrollments = (
        Enrollment.query.filter_by(student=student_id)
        .join(Instructor)
        .join(Course)
        .all()
    )
    response = []
    for e in enrollments:
        enrollment_data = e.__dict__
        instructor_data = get_instructor_bypk(e.instructor)
        course_data = get_course(e.course)
        enrollment_data['instructor'] = instructor_data
        enrollment_data['course'] = course_data
        response.append(enrollment_data)
    return response

def get_student_enrollment_options(student_id):
    enrolled_classes = get_student_enrollments(student_id)
    all_courses = [u.__dict__ for u in Course.query.all()]
    existing_courses_ids = [c['course']['id'] for c in enrolled_classes]
    available_courses = [course for course in all_courses if course['id'] not in existing_courses_ids]
    response = {
        'student': get_student_bypk(student_id),
        'available_courses': available_courses,
        'instructors': get_instructors(),
        'enrolled': enrolled_classes
    }
    return response

def upload_receipt(user_id, file):
    student = Student.query.filter_by(user=user_id).first()
    student.receipt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts', 'receipt_' + str(user_id) + '.jpg')
    file.data.save(student.receipt_filepath)
    db.session.commit()

def upload_document(user_id, file):
    student = Student.query.filter_by(user=user_id).first()
    student.document_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', 'document_' + str(user_id) + '.pdf')
    file.data.save(student.document_filepath)
    db.session.commit()

def move_student_progress(student_id, progress):
    student = Student.query.filter_by(id=student_id).first()
    if student.progress == progress:
        if progress == 'payment':
            student.progress = 'evaluation'
        elif progress == 'evaluation':
            student.progress = 'enrollment'
        else:
            student.progress = 'completion'
        db.session.commit()
        return "Success."
    else:
        return "Invalid operation."
    
def get_enrollment(id):
    return Enrollment.query.filter_by(id=id).first().__dict__

def add_course(course):
    new_course = Course(
        title = course['title'],
        code = course['code']
    )
    db.session.add(new_course)
    db.session.commit()

def get_course(cid):
    return Course.query.filter_by(id=cid).first().__dict__

def get_courses():
    return [u.__dict__ for u in Course.query.all()]

def enroll_student(student_id, data):
    new_enrollment = Enrollment(
        course = data['courses_select'],
        student = student_id,
        instructor = uid_to_pk(data['instructors_select'], 'instructor'),
        status = 'pending'
    )
    db.session.add(new_enrollment)
    db.session.commit()
    course_str = str(get_course(data['courses_select'])['code'])
    inst_dict = get_instructor(data['instructors_select'])
    inst_name = f"{inst_dict['l_name'].capitalize()}, {inst_dict['f_name']} {inst_dict['m_name']}."
    return f"Enrolled student in {course_str} under {inst_name}"

def _remove_sa_instance_state(obj):
    if isinstance(obj, list):
        return [_remove_sa_instance_state(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _remove_sa_instance_state(value) for key, value in obj.items() if key != '_sa_instance_state'}
    else:
        return obj