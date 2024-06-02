from app import app, db
from models import *
from sqlalchemy import func
from uuid import uuid4
import os
import sys
import json
from datetime import date
from pathlib import Path

def _calculate_age(birthyear, birthmonth, birthday):
    today = date.today()
    birth_date = date(year=birthyear, month=birthmonth, day=birthday)
    age = today.year - birthyear
    if (today.month, today.day) < (birthmonth, birthday):
        age -= 1
    return age

def get_system_settings():
    fp = "./cfg.json"
    if os.path.exists(fp):
        with open(fp, 'r') as file:
            cfg = json.loads(file.read())
    else:
        cfg = {'academic_year': date.today().year, 'semester': '1st'}
        with open(fp, 'w') as file:
            file.write(json.dumps(cfg))
    return cfg

def update_system_settings(data):
    try:
        fp = "./cfg.json"
        cfg = {
            'academic_year': data['academic_year'],
            'semester': data['semester']
        }
        with open(fp, 'w') as file:
            file.write(json.dumps(cfg))
        return True, "Updated system settings." 
    except Exception as e:
        return False, "Unable to update system settings." 

def get_user(user_id):
    return User.query.filter_by(id=user_id).first().__dict__

def get_users(user_type):
    return [u.__dict__ for u in User.query.filter_by(user_type=user_type).all()]

def get_account_details(user_id):
    user = User.query.filter_by(id=user_id).first().__dict__
    if user['user_type'] == 'student':
        student = Student.query.filter_by(user=user_id).first().__dict__
        user['tup_id'] = student['tup_id']
    if user['user_type'] == 'instructor':
        instructor = Instructor.query.filter_by(user=user_id).first().__dict__
        college = College.query.filter_by(id=instructor['college']).first().abbr
        user['college'] = college
        user['educational_background'] = get_educational_background(user_id)
    return user

def update_account_details(user_id, data):
    try:
        for key, value in data.items():
            if value == "None":
                data[key] = None
        user = User.query.filter_by(id=user_id).first()
        user.l_name = data['l_name']
        user.f_name = data['f_name']
        user.m_name = data['m_name']
        user.ext_name = data['ext_name']
        user.civil_status = data['civil_status']
        user.citizenship = data['citizenship']
        user.birthmonth = data['birthmonth']
        user.birthday = data['birthday']
        user.birthyear = data['birthyear']
        user.gender = data['gender']
        user.email = data['email']
        user.contact_no = data['contact_no']
        user.residency = data['residency']
        user.local_address = data['local_address']
        user.foreign_address = data['foreign_address']
        if user.user_type == 'student':
            student = Student.query.filter_by(user=user_id).first()
            student.tup_id = data['tup_id']
        elif user.user_type == 'instructor':
            instructor = Instructor.query.filter_by(user=user_id).first()
            college_id = College.query.filter_by(abbr=data['college']).first().id
            instructor.college = college_id
        db.session.commit()
        return True, "Account details have been changed."
    except Exception as e:
        return False, f"An error occured while trying to update account. {e}"

import string
import random

def reset_password(id):
    try:
        user = User.query.filter_by(id=id).first()
        characters = string.ascii_letters
        new_password = ''.join(random.choice(characters) for i in range(6))
        user.reset_password = True
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        name = f"{user.f_name} {user.l_name}"
        return True, f"Password for {name} has been reset. New password {new_password}"
    except Exception as e:
        return False, f"Unable to reset password. {e}" 

def set_new_password(id, data):
    try:
        user = User.query.filter_by(id=id).first()
        user.password = data['password']
        user.reset_password = False
        db.session.add(user)
        db.session.commit()
        return True, f"Password saved."
    except:
        return False, f"Password was not saved." 

def add_educational_background(uid, data):
    instructor = Instructor.query.filter_by(user=uid).first()
    if data['school'] and data['degree'] and data['start_year'] and data['end_year']:
        new_educational_background = EducationalBackground(
            school = data['school'],
            degree = data['degree'],
            start_year = data['start_year'],
            end_year = data['end_year'],
            academic_honors = data['academic_honors'],
            instructor = instructor.user
        )
        db.session.add(new_educational_background)
        db.session.commit()

def update_educational_background(data):
    educational_background = EducationalBackground.query.filter_by(id=data['id']).first()
    educational_background.school = data['school']
    educational_background.degree = data['degree']
    educational_background.start_year = data['start_year']
    educational_background.end_year = data['end_year']
    educational_background.academic_honors = data['academic_honors']
    db.session.commit()

def get_educational_background(uid):
    instructor = Instructor.query.filter_by(user=uid).first()
    educational_backgrounds = EducationalBackground.query.filter_by(instructor=instructor.user).all()
    response = []
    for e in educational_backgrounds:
        response.append(e.__dict__)
    return response

def complete_ft_login(user_id, data):
    try:
        user = User.query.filter_by(id=user_id).first()
        user.password = data['password']
        if user.user_type == 'student':
            student = Student.query.filter_by(user=user_id).first()
            if student.tup_id != data['tup_id']:
                return False, "Invalid TUP ID."
        update_account_details(user_id, data)
        user.ft_login = False
        db.session.commit()
        return True, "Account Details Saved."
    except Exception as e:
        return False, f"An error occured trying to save account details."

def change_password(user_id, data):
    try:
        user = User.query.filter_by(id=user_id).first()
        if user.password == data['current']:
            user.password = data['new']
            db.session.commit()
            return True, "Password changed."
        else:
            return False, "Incorrect password."
    except Exception as e:
        return False, "An error occured when trying to save password."

def generate_student_report(filters):
    students = get_students()
    data = {
        'total_enrollees': 0,
    }
    if filters['age']:
        data['age'] = {}
    if filters['gender']:
        data['gender'] = {}
    if filters['residency']:
        data['residency'] = {}
    if filters['student_course_status']:
        data['course_status'] = {}
    for student in students:
        # get student info
        user = get_user(user_id=student['user'])
        ay = str(student['ay'])
        semester = str(student['semester'])
        program = Program.query.filter_by(id=student['program']).first()
        if program == None:
            continue
        else:
            college = College.query.filter_by(id=program.college_id).first()
            program = program.abbr
            if college == None:
                continue
            else:
                college = college.abbr
        # skip if student doesn't match filter
        if filters['ay'] != "All" and ay != filters['ay']:
            continue
        if filters['semester'] != "All" and semester != filters['semester']:
            continue
        if filters['college'] != "All" and college != filters['college']:
            continue
        if filters['program'] != "All" and program != filters['program']:
            continue
        data['total_enrollees'] += 1
        # store data
        if 'age' in data.keys():
            if user['birthyear'] and user['birthmonth'] and user['birthday']:
                age = _calculate_age(user['birthyear'], user['birthmonth'], user['birthday'])
                if age not in data['age']:
                    data['age'][age] = 0
                data['age'][age] += 1
        if 'gender' in data.keys():
            gender = user['gender']
            if gender not in data['gender']:
                data['gender'][gender] = 0
            data['gender'][gender] += 1
        if 'residency' in data.keys():
            if user['residency'] != None:
                residency = user['residency']
                if residency not in data['residency']:
                    data['residency'][residency] = 0
                data['residency'][residency] += 1
        if 'course_status' in data.keys():
            subjects = Enrollment.query.filter_by(student=student['id']).all()
            for subject in subjects:
                if subject.status not in data['course_status']:
                    data['course_status'][subject.status] = 0
                data['course_status'][subject.status] += 1
            order = ['pending', 'ongoing', 'completed']
            sorted_course_status = {key: data['course_status'][key] for key in order}
            data['course_status'] = sorted_course_status
    if 'age' in data.keys():
        data['age'] = dict(sorted(data['age'].items()))
    return data

def generate_faculty_report(filters):
    data = {
        'faculty': []
    }
    instructors = get_instructors()
    for instructor in instructors:
        college = instructor['college']
        if filters['college'] != "All" and college != filters['college']:
            continue
        user = User.query.filter_by(id=instructor['user']).first()
        enrollments = Enrollment.query.filter_by(instructor=instructor['id']).all()
        name = f"{user.l_name} {user.f_name} {user.m_name if user.m_name else ''}"
        pending = []
        ongoing = []
        completed = []
        honorarium_released = []
        honorarium_onprocess = []
        for enrollment in enrollments:
            ay = enrollment.ay
            semester = enrollment.semester
            if filters['ay'] != "All" and ay != filters['ay']:
                continue
            if filters['semester'] != "All" and semester != filters['semester']:
                continue
            course = Course.query.filter_by(id=enrollment.course).first()
            course_name = course.code
            student = Student.query.filter_by(id=enrollment.student).first()
            student = User.query.filter_by(id=student.user).first()
            student_name = f"{student.l_name} {student.f_name} {student.m_name} "
            if enrollment.status == 'pending':
                pending.append({'course': course_name, 'student': student_name})
            elif enrollment.status == 'ongoing':
                ongoing.append({'course': course_name, 'student': student_name})
            else:
                completed.append({'course': course_name, 'student': student_name})
            if enrollment.honorarium == 'onprocess':
                honorarium_onprocess.append({'course': course_name, 'student': student_name})
            else:
                honorarium_released.append({'course': course_name, 'student': student_name})
        snapshot = {'name': name}
        if filters['faculty_course_status']:
            snapshot['pending'] = {'count': len(pending), 'enrollments': pending}
            snapshot['ongoing'] = {'count': len(ongoing), 'enrollments': ongoing}
            snapshot['completed'] = {'count': len(completed), 'enrollments': completed}
        if filters['honorarium']:
            snapshot['honorarium_released'] = {'count': len(honorarium_released), 'enrollments': honorarium_released}
            snapshot['honorarium_onprocess'] = {'count': len(honorarium_onprocess), 'enrollments': honorarium_onprocess}
        data['faculty'].append(snapshot)
    return data

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows 
import os

def create_sheet(data, wb, total_enrollees, sheet_name, Category):
    
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    ws = wb.create_sheet(title=sheet_name)
        
    ws.append(["Total Enrollees", total_enrollees])
    ws.append([])
    df = pd.DataFrame(data, columns=[Category, "Count"])
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    chart = BarChart()
    chart.title = sheet_name
    chart.x_axis.title = Category
    chart.y_axis.title = "Count"

    chart.width = 30
    chart.height = 15
    
    temp = Reference(ws, min_col=2, min_row=3, max_col=len(df.columns), max_row=len(df) + 3)
    categories = Reference(ws, min_col=1, min_row=4, max_row=len(df) + 3)
    chart.add_data(temp, titles_from_data=True)
    chart.set_categories(categories)

    ws.add_chart(chart, "E6")

def create_student_excel(file_name, data):
    try:
        excel_file = f'{file_name}.xlsx'

        if os.path.exists(excel_file):
            os.remove(excel_file)

        wb = Workbook()
        wb.remove(wb.active)

        # Age
        if "age" in data:
            create_sheet(data["age"].items(), wb, data["total_enrollees"],  "Age Distribution", "Age")
        # Gender
        if "gender" in data:
            create_sheet(data["gender"].items(), wb, data["total_enrollees"], "Gender Distribution", "Gender")
        # Residency
        if "residency" in data:
            create_sheet(data["residency"].items(), wb, data["total_enrollees"], "Residency Distribution", "Residency")
        # Course_Status
        if "course_status" in data:
            create_sheet(data["course_status"].items(), wb, data["total_enrollees"], "Course Status Distribution", "Course Status")

        # Auto Fit
        for sheet in wb.worksheets:
            for column in sheet.columns:
                max_length = 7.15
                column = list(column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width

        wb.save(excel_file)
        return True, "Report created."
    except Exception as e:
        return False, f"Problem occured while generating report. {e}"

def create_faculty_excel(file_name, data):
    try:
        # Lists faculty members and the subjects they handle. Includes details on the number of subjects completed and ongoing for each faculty member.
        excel_file = f'{file_name}.xlsx'
        if os.path.exists(excel_file):
            os.remove(excel_file)

        wb = Workbook()
        wb.remove(wb.active)

        if "pending" in data["faculty"][0]:
            new_sheet_name = 'Faculty - Subjects'
            if new_sheet_name in wb.sheetnames:
                del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)

            flattened_data = []
            for faculty in data["faculty"]:
                courses_handled = []
                for enrollment_type in ["pending", "ongoing", "completed"]:
                    for enrollment in faculty[enrollment_type]["enrollments"]:
                        courses_handled.append(enrollment["course"])
                flattened_data.append({
                    "Faculty Name": faculty["name"], 
                    "Courses Handled": ", ".join(courses_handled),
                    "Pending": faculty["pending"]["count"],
                    "Ongoing": faculty["ongoing"]["count"],
                    "Completed": faculty["completed"]["count"],
                    "Courses Count": len(courses_handled),
                    })

            df = pd.DataFrame(flattened_data)

            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)

            
            chart = BarChart()
            chart.title = "Faculty Distribution"
            chart.x_axis.title = "Faculty"
            chart.y_axis.title = "Count"

            chart.width = 30
            chart.height = 15

            temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
            categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
            chart.add_data(temp, titles_from_data=True)
            chart.set_categories(categories)

            ws.add_chart(chart, f"B{len(df)+ 3}")

        # Honorarium
        if "honorarium_onprocess" in data["faculty"][0]:
            new_sheet_name = 'Honorarium'
            if new_sheet_name in wb.sheetnames:
                del wb[new_sheet_name]
            
            ws = wb.create_sheet(title=new_sheet_name)

            flattened_data = []
            for student in data["faculty"]:
                flattened_data.append({
                    "Faculty Name": student["name"],
                    "Honorarium Released": student["honorarium_released"]["count"],
                    "Honorarium Onprocess": student["honorarium_onprocess"]["count"]
                })

            df = pd.DataFrame(flattened_data)

            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)

            chart = BarChart()
            chart.title = "Honorarium Distribution"
            chart.x_axis.title = "Faculty"
            chart.y_axis.title = "Count"

            chart.width = 30
            chart.height = 15

            temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
            categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
            chart.add_data(temp, titles_from_data=True)
            chart.set_categories(categories)

            ws.add_chart(chart, f"B{len(df)+ 3}")

        # Auto Fit
        for sheet in wb.worksheets:
            for column in sheet.columns:
                max_length = 7.15
                column = list(column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[get_column_letter(column[0].column)].width = adjusted_width

        wb.save(excel_file)
        return True, "Report created."
    except Exception as e:
        return False, f"Problem occured while generating report. {e}"

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

def add_user(data):
    try:
        for key, value in data.items():
            if value == "None":
                data[key] = None
        new_user = User(
            username=data['username'], 
            f_name=data['f_name'],
            m_name=data['m_name'],
            l_name=data['l_name'],
            ext_name=data['ext_name'],
            gender=data['gender'],
            password=data['password'],
            user_type=data['user_type']
        )
        db.session.add(new_user)
        db.session.commit()
        if data['user_type'] == "admin":
            new_admin = Admin(user=new_user.id)
            db.session.add(new_admin)
        elif data['user_type'] == "instructor":
            college_id = College.query.filter_by(abbr=data['college']).first().id
            new_instructor = Instructor(user=new_user.id, college=college_id)
            db.session.add(new_instructor)
        else:
            cfg = get_system_settings()
            new_student = Student(
                user=new_user.id, 
                tup_id=data['tup_id'],
                ay=cfg['academic_year'],
                semester=cfg['semester']
            )
            db.session.add(new_student)
        db.session.commit()
        return True, "Successfully added user."
    except Exception as e:
        return False, f"Error occured while adding user."

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
        instructor['college'] = College.query.filter_by(id=instructor['college']).first().abbr
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

def get_academic_years():
    enrollments = Enrollment.query.all()
    academic_years = []
    for enrollment in enrollments:
        if enrollment.ay not in academic_years:
            academic_years.append(enrollment.ay)
    return academic_years

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
    response = Requirement.query.filter_by(id=requirement_id).first().__dict__
    response['materials'] = get_materials(requirement_id)
    response['description'] = response['description'].split('\n')
    response['submissions'] = get_submissions(requirement_id)
    return response

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
            filename = str(uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'materials', filename)
            file.save(filepath)
            new_material = RequirementMaterial(filepath=filepath, filename=file.filename, requirement=new_requirement.id)
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

def add_submission(requirement_id, form):
    try:
        for file in form.submissions.data:
            filename = str(uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'submissions', filename)
            file.save(filepath)
            new_submission = RequirementSubmission(filepath=filepath, filename=file.filename, requirement=requirement_id)
            db.session.add(new_submission)
        db.session.commit()
        return "Requirement posted."
    except Exception as e:
        db.session.rollback()
        return f"An error occured while posting the requirement: {e}"

def turn_in_submission(requirement_id):
    requirement = Requirement.query.filter_by(id=requirement_id).first()
    if requirement.progress == 'incomplete':
        requirement.progress = 'evaluation'
        db.session.commit()
        return "Successfully turned in."
    else:
        return "Invalid operation."
    
def return_submission(requirement_id):
    requirement = Requirement.query.filter_by(id=requirement_id).first()
    if requirement.progress == 'evaluation':
        requirement.progress = 'completed'
        db.session.commit()
        return "Successfully returned."
    else:
        return "Invalid operation."

def get_student(user_id):
    student = Student.query.filter_by(user=user_id).first().__dict__
    userinfo = get_user(student['user'])
    student['f_name'] = userinfo['f_name']
    student['l_name'] = userinfo['l_name']
    student['m_name'] = userinfo['m_name']
    if userinfo['ext_name'] not in [None, "None"]:
        student['ext_name'] = userinfo['ext_name']
    student['username'] = userinfo['username']
    return student

def get_student_bypk(id):
    student = Student.query.filter_by(id=id).first().__dict__
    userinfo = get_user(student['user'])
    student['f_name'] = userinfo['f_name']
    student['l_name'] = userinfo['l_name']
    student['m_name'] = userinfo['m_name']
    if userinfo['ext_name'] not in [None, "None"]:
        student['ext_name'] = userinfo['ext_name']
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
        'programs': get_programs(),
        'available_courses': available_courses,
        'instructors': get_instructors(),
        'enrolled': enrolled_classes
    }
    return response

def upload_receipt(user_id, data):
    student = Student.query.filter_by(user=user_id).first()
    student.receipt_filepath = str(uuid4()) + os.path.splitext(data['file'].filename)[1]
    fp = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts', student.receipt_filepath)
    data['file'].save(fp)
    db.session.commit()

def get_receipt_fp(user_id):
    student = Student.query.filter_by(user=user_id).first()
    fp = student.receipt_filepath
    return fp

def move_student_progress(student_id, progress):
    student = Student.query.filter_by(id=student_id).first()
    if student.progress == progress:
        if progress == 'payment':
            student.progress = 'enrollment'
        else:
            student.progress = 'graduate'
        db.session.commit()
        return True, "Documents have been approved."
    else:
        return False, "Invalid operation."
    
def get_enrollment(id):
    return Enrollment.query.filter_by(id=id).first().__dict__

def get_programs_by_college():
    response = []
    for c in College.query.all():
        c = c.__dict__
        c['programs'] = [p.__dict__ for p in Program.query.filter_by(college_id=c['id']).all()]
        response.append(c)
    return response

def get_programs():
    return [p.__dict__ for p in Program.query.all()]

def get_program(program_id):
    program = Program.query.filter_by(id=program_id).first()
    if program:
        return program.__dict__
    else:
        return {
            'id': None,
            'name': 'Not yet enrolled to any program.',
            'abbr': 'Not yet enrolled to any program.',
            'courses': [],
            'college_id': None
        }

def add_course(course):
    try:
        new_course = Course(
            title = course['title'],
            code = course['code']
        )
        db.session.add(new_course)
        db.session.commit()
        return True, "Added new course."
    except:
        return False, "Error occured while adding course."

def get_course(cid):
    return Course.query.filter_by(id=cid).first().__dict__

def get_courses():
    return [u.__dict__ for u in Course.query.all()]

def enroll_student_in_course(student_id, data):
    student = Student.query.filter_by(id=student_id).first()
    new_enrollment = Enrollment(
        course = data['courses_select'],
        student = student_id,
        ay = student.ay,
        semester = student.semester,
        instructor = uid_to_pk(data['instructors_select'], 'instructor'),
        status = 'pending'
    )
    db.session.add(new_enrollment)
    db.session.commit()
    course_str = str(get_course(data['courses_select'])['code'])
    inst_dict = get_instructor(data['instructors_select'])
    inst_name = f"{inst_dict['l_name'].capitalize()}, {inst_dict['f_name']} {inst_dict['m_name']}."
    return f"Enrolled student in {course_str} under {inst_name}"

def enroll_student_in_program(student_id, data):
    student = Student.query.filter_by(id=student_id).first()
    student.ay = data['academic_year']
    student.semester = data['semester']
    student.program = data['programs_select']
    db.session.commit()
    program_info = get_program(data['programs_select'])
    return f"Enrolled student in {program_info['abbr']} for {data['semester']} Semester Academic Year {data['academic_year']}"

def submit_grade(enrollment_id, data):
    try:
        enrollment = Enrollment.query.filter_by(id=enrollment_id).first()
        enrollment.grade = data['grade']
        enrollment.status = 'completed'
        file1name = str(uuid4()) + os.path.splitext(data['file1'].filename)[1]
        file1path = os.path.join(app.config['UPLOAD_FOLDER'], 'grades', file1name)
        data['file1'].save(file1path)
        enrollment.form1 = file1name
        file2name = str(uuid4()) + os.path.splitext(data['file2'].filename)[1]
        file2path = os.path.join(app.config['UPLOAD_FOLDER'], 'grades', file2name)
        data['file2'].save(file2path)
        enrollment.form2 = file2name
        file3name = str(uuid4()) + os.path.splitext(data['file3'].filename)[1]
        file3path = os.path.join(app.config['UPLOAD_FOLDER'], 'grades', file3name)
        data['file3'].save(file3path)
        enrollment.form3 = file3name
        db.session.add(enrollment)
        db.session.commit()
        return True, f"Grades have been submitted."
    except Exception as e:
        return False, f"Error: {e}."

def release_honorarium(enrollment_id):
    try:
        enrollment = Enrollment.query.filter_by(id=enrollment_id).first()
        enrollment.honorarium = 'released'
        db.session.add(enrollment)
        db.session.commit()
        return True, f"Honorarium has been released."
    except Exception as e:
        return False, f"Problem occred when releasing honorarium."

def _remove_sa_instance_state(obj):
    if isinstance(obj, list):
        return [_remove_sa_instance_state(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _remove_sa_instance_state(value) for key, value in obj.items() if key != '_sa_instance_state'}
    else:
        return obj