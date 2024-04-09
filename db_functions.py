from app import app, db
from models import *
from sqlalchemy import func
import os

def get_user(user_id):
    return User.query.filter_by(id=user_id).first().__dict__

def get_users(user_type):
    return [u.__dict__ for u in User.query.filter_by(user_type=user_type).all()]

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
        new_admin = Admin(user_id=new_user.id)
        db.session.add(new_admin)
    elif user['user_type'] == "instructor":
        new_instructor = Instructor(user_id=new_user.id)
        db.session.add(new_instructor)
    else:
        new_student = Student(user_id=new_user.id)
        db.session.add(new_student)
    db.session.commit()

def upload_receipt(user_id, file):
    student = Student.query.filter_by(user_id=user_id).first()
    student.receipt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts', 'receipt_' + str(user_id) + '.jpg')
    file.data.save(student.receipt_filepath)
    db.session.commit()

def upload_document(user_id, file):
    student = Student.query.filter_by(user_id=user_id).first()
    student.document_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'documents', 'document_' + str(user_id) + '.pdf')
    file.data.save(student.document_filepath)
    db.session.commit()

def get_instructor(user_id):
    instructor = Instructor.query.filter_by(user_id=user_id).first().__dict__
    userinfo = get_user(instructor['user_id'])
    instructor['f_name'] = userinfo['f_name']
    instructor['l_name'] = userinfo['l_name']
    instructor['m_name'] = userinfo['m_name']
    instructor['username'] = userinfo['username']
    return instructor

def get_instructor_bypk(id):
    instructor = Instructor.query.filter_by(id=id).first().__dict__
    userinfo = get_user(instructor['user_id'])
    instructor['f_name'] = userinfo['f_name']
    instructor['l_name'] = userinfo['l_name']
    instructor['m_name'] = userinfo['m_name']
    instructor['username'] = userinfo['username']
    return instructor

def get_instructors():
    instructors = []
    for instructor in Instructor.query.all():
        instructor = instructor.__dict__
        userinfo = get_user(instructor['user_id'])
        instructor['f_name'] = userinfo['f_name']
        instructor['l_name'] = userinfo['l_name']
        instructor['m_name'] = userinfo['m_name']
        instructor['username'] = userinfo['username']
        instructors.append(instructor)
    return instructors

def get_student(user_id):
    student = Student.query.filter_by(user_id=user_id).first().__dict__
    userinfo = get_user(student['user_id'])
    student['f_name'] = userinfo['f_name']
    student['l_name'] = userinfo['l_name']
    student['m_name'] = userinfo['m_name']
    student['username'] = userinfo['username']
    return student

def get_students():
    students = []
    for student in Student.query.all():
        student = student.__dict__
        userinfo = get_user(student['user_id'])
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

def move_student_progress(user_id, progress):
    student = Student.query.filter_by(user_id=user_id).first()
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
    
def get_student_classes(user_id):
    classes = (
        db.session.query(Class)
        .join(enrollment, Class.id == enrollment.c.class_id)
        .join(Student, Student.id == enrollment.c.student_id)
        .join(Course, Class.course == Course.id)
        .filter(Student.user_id == user_id)
        .all()
    )
    response = []
    for c in classes:
        c = c.__dict__
        c['course'] = get_course(str(c['course']))
        c['instructor'] = get_instructor_bypk(c['instructor'])
        response.append(c)
    return response

def get_student_enrollment_options(user_id):
    enrolled_classes = get_student_classes(user_id)
    all_courses = [u.__dict__ for u in Course.query.all()]
    existing_courses_ids = [c['course']['id'] for c in enrolled_classes]
    available_courses = [course for course in all_courses if course['id'] not in existing_courses_ids]
    response = {
        'student': get_student(user_id),
        'available_courses': available_courses,
        'instructors': get_instructors(),
        'enrolled': enrolled_classes
    }
    return _remove_sa_instance_state(response)

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

def enroll_student(user_id, data):
    course_id = data['courses_select']
    instructor_id = data['instructors_select']
    student = Student.query.filter_by(user_id=user_id).first()
    instructor = Instructor.query.filter_by(user_id=instructor_id).first()
    existing_class = db.session.query(Class).filter(Class.course == course_id, Class.instructor == instructor_id).first()
    if not existing_class:
        new_class = Class(
            course = data['courses_select'],
            instructor = data['instructors_select'],
        )
    student.classes.append(new_class)
    instructor.classes.append(new_class)
    db.session.commit()
    course_str = str(get_course(data['courses_select'])['code'])
    inst_dict = get_instructor(instructor_id)
    inst_name = f"{inst_dict['l_name'].capitalize()}, {inst_dict['f_name']} {inst_dict['m_name']}."
    return f"Enrolled student in {course_str} under {inst_name}"

def _remove_sa_instance_state(obj):
    if isinstance(obj, list):
        return [_remove_sa_instance_state(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _remove_sa_instance_state(value) for key, value in obj.items() if key != '_sa_instance_state'}
    else:
        return obj