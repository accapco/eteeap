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

def get_courses():
    return [u.__dict__ for u in Course.query.all()]

def add_course(course):
    new_course = Course(
        title = course['title'],
        code = course['code']
    )
    db.session.add(new_course)
    db.session.commit()

def get_student(user_id):
    return Student.query.filter_by(user_id=user_id).first().__dict__

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