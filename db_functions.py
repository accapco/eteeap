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
    return user

def complete_ft_login(user_id, data):
    try:
        user = User.query.filter_by(id=user_id).first()
        user.password = data['password']
        user.ft_login = False
        if user.user_type == 'student':
            student = Student.query.filter_by(user=user_id).first()
            if student.tup_id != data['tup_id']:
                return False, "Invalid TUP ID."
        db.session.commit()
        return True, "Password saved."
    except Exception as e:
        return False, f"An error occured when trying to save password."

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

from copy import deepcopy

def generate_report():
        students = get_students()
        instructors = get_instructors()
        data = {
            'total_enrollees': {},
            'per_program': {
            },
            'per_college': {
            },
            'per_period': {},
            'faculty': [],
            'per_student': [],
            'course_completion': []
        }
        programs_per_college = {}
        colleges = {}
        for college in College.query.all():
            colleges[college.abbr] = 0
            programs_per_college[college.abbr] = {}
        data['per_college'] = colleges
        programs = {}
        for program in Program.query.all():
            programs[program.abbr] = 0
            college = College.query.filter_by(id=program.college_id).first()
            programs_per_college[college.abbr][program.abbr] = {
                "total_count": 0,
                "male": 0,
                "female": 0,
                "local": 0,
                "foreign": 0,
                "ages": {}
            }
        data['per_program'] = programs
        for student in students:
            user = User.query.filter_by(id=student['user']).first()
            user = user.__dict__
            student['gender'] = user['gender']
            student['citizenship'] = user['citizenship']
            # total_enrollees
            if student['ay'] != None:
                if student['ay'] not in data['total_enrollees'].keys():
                    data['total_enrollees'][student['ay']] = {"1st": 0, "2nd": 0}
                if student['semester'] != None:
                    data['total_enrollees'][student['ay']][student['semester']] += 1
            # per program
            program = Program.query.filter_by(id=student['program']).first()
            if program != None:
                abbr = program.abbr
                data['per_program'][abbr] += 1
            # per college
            if program != None:
                college = College.query.filter_by(id=program.college_id).first()
                abbr = college.abbr
                data['per_college'][abbr] += 1
            # per period
            if student['ay'] != None and student['semester'] != None and student['program'] != None:
                if student['ay'] not in data['per_period'].keys():
                    data['per_period'][student['ay']] = {"1st": deepcopy(programs_per_college), "2nd": deepcopy(programs_per_college)}
                program = Program.query.filter_by(id=student['program']).first()
                college = College.query.filter_by(id=program.college_id).first()
                data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['total_count'] += 1
                # demographic
                # gender
                if student['gender'] == 'M':
                    data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['male'] += 1
                elif student['gender'] == 'F':
                    data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['female'] += 1
                # citizenship
                if student['citizenship'] != None and student['citizenship'].lower() == 'filipino':
                    data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['local'] += 1
                elif student['citizenship'] != None: 
                    data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['foreign'] += 1
                # age
                if user['birthyear'] and user['birthmonth'] and user['birthday']:
                    age = _calculate_age(user['birthyear'], user['birthmonth'], user['birthday'])
                    if age not in data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['ages'].keys():
                        data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['ages'][age] = 0
                    data['per_period'][student['ay']][student['semester']][college.abbr][program.abbr]['ages'][age] += 1
            # per student
            name = f"{user['l_name']} {user['f_name']} {user['m_name']}"
            enrollments = Enrollment.query.filter_by(student=student['id']).all()
            subjects = {
                'pending': 0,
                'ongoing': 0,
                'completed': 0
            }
            for enrollment in enrollments:
                course = Course.query.filter_by(id=enrollment.course).first()
                course_name = course.code
                subjects[enrollment.status] += 1
            data['per_student'].append({'name': name, 'subjects': subjects})
        # course completion rate
        courses = Course.query.all()
        for course in courses:
            enrollments = [e.__dict__ for e in Enrollment.query.filter_by(course=course.id).all() if e.status != 'pending']
            if len(enrollments) > 0:
                ongoing = len([e for e in enrollments if e['status'] == 'ongoing'])
                completed = len([e for e in enrollments if e['status'] == 'completed'])
                data['course_completion'].append({
                    'name': course.code,
                    'ongoing': ongoing,
                    'completed': completed,
                    'percentage': completed / (ongoing+completed) * 100
                })
        # faculty
        for instructor in instructors:
            user = User.query.filter_by(id=instructor['user']).first()
            enrollments = Enrollment.query.filter_by(instructor=instructor['id']).all()
            name = f"{user.l_name} {user.f_name} {user.m_name}"
            pending = []
            ongoing = []
            completed = []
            for enrollment in enrollments:
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
            data['faculty'].append({ 
                'name': name,
                'pending': {'count': len(pending), 'enrollments': pending},
                'ongoing': {'count': len(ongoing), 'enrollments': ongoing},
                'completed': {'count': len(completed), 'enrollments': completed},
            })
        return data

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows 
import os

def create_excel(data):
    try:
        excel_file = 'reports.xlsx'
        if os.path.exists(excel_file):
            wb = load_workbook(excel_file)
        else:
            wb = Workbook()
            wb.remove(wb.active)

        # Number of Enrollees per Semester, Academic Year
        new_sheet_name = 'Number of Enrollees'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for year, period in data["total_enrollees"].items():
            for period, count in period.items():
                flattened_data.append({
                    "Year-Period": f"{year} - {period} semester",
                    "Count": count
                })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Number of Enrollees"
        chart.x_axis.title = "Year-Period"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")
        # College Enrollment Summary
        new_sheet_name = 'Number of Enrollees Per Program'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        df = pd.DataFrame(list(data["per_program"].items()), columns=["Program", "Count"])

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Program Distribution"
        chart.x_axis.title = "Program"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")

        # Program Enrollment Breakdown
        new_sheet_name = 'Per College'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        df = pd.DataFrame(list(data["per_college"].items()), columns=["College", "Count"])

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "College Distribution"
        chart.x_axis.title = "College"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")

        # Comparison with Previous Periods
        new_sheet_name = 'Per Period'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for year, periods in data["per_period"].items():
            for period, colleges in periods.items():
                for college, programs in colleges.items():
                    for program, counts in programs.items():
                        flattened_data.append({
                            "Year - Period - College - Program": f"{year}-{period} semester-{college}-{program}",
                            "Total Count": counts["total_count"]
                        })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Period Distribution"
        chart.x_axis.title = "Year - Period - College - Program"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")

        # Age
        new_sheet_name = 'Age'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for year, periods in data["per_period"].items():
            for period, colleges in periods.items():
                for college, programs in colleges.items():
                    for program, details in programs.items():
                        for age, count in details['ages'].items():
                            key = f"{year}-{period}-{age}"
                            existing = next((item for item in flattened_data if item["Year-Period-Age"] == key), None)
                            if existing:
                                existing["Age Count"] += count
                            else:
                                flattened_data.append({
                                    "Year-Period-Age": key,
                                    "Age Count": count,
                                })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Age Distribution"
        chart.x_axis.title = "Year-Period-Age"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")

        # Gender
        new_sheet_name = 'Gender'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for year, periods in data["per_period"].items():
            for period, colleges in periods.items():
                male_count = 0
                female_count = 0

                for college, programs in colleges.items():
                    for program, counts in programs.items():
                        male_count += counts["male"]
                        female_count += counts["female"]
                
                flattened_data.append({
                    "Year-Period": f"{year}-{period} semester",
                    "Male Count": male_count,
                    "Female Count": female_count
                })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Gender Distribution"
        chart.x_axis.title = "Year-Period"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")

        # Lists faculty members and the subjects they handle. Includes details on the number of subjects completed and ongoing for each faculty member.
        new_sheet_name = 'Faculty - Subjects'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
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
                "Courses Count": len(courses_handled)
                })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Courses Distribution"
        chart.x_axis.title = "Faculty"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "H6")

        # Provides a breakdown of the number of subjects completed and ongoing for each student.
        new_sheet_name = 'Student - Subjects'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for student in data["per_student"]:
            flattened_data.append({
                "Student Name": student["name"],
                "Pending": student["subjects"]["pending"],
                "Ongoing": student["subjects"]["ongoing"],
                "Completed": student["subjects"]["completed"],
                "Total Subjects": student["subjects"]["pending"] + student["subjects"]["completed"] + student["subjects"]["ongoing"]
            })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Student Subjects Distribution"
        chart.x_axis.title = "Students"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "G6")

        # Number of Students Categorized (Foreign and Local)
        new_sheet_name = 'Local or Foreign'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for year, periods in data["per_period"].items():
            for period, colleges in periods.items():
                local_count = 0
                foreign_count = 0

                for college, programs in colleges.items():
                    for program, counts in programs.items():
                        local_count += counts["local"]
                        foreign_count += counts["foreign"]
                
                flattened_data.append({
                    "Year-Period": f"{year}-{period} semester",
                    "Local Count": local_count,
                    "Foreign Count": foreign_count
                })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        chart = BarChart()
        chart.title = "Citizenship Distribution"
        chart.x_axis.title = "Year-Period"
        chart.y_axis.title = "Count"

        temp = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=len(df) + 1)
        categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)
        chart.add_data(temp, titles_from_data=True)
        chart.set_categories(categories)

        ws.add_chart(chart, "E6")


        # Provides insights into the percentage of enrolled students who successfully complete each course within their ETEEAP program.
        new_sheet_name = 'Course Completion'
        if new_sheet_name in wb.sheetnames:
            del wb[new_sheet_name]
            ws = wb.create_sheet(title=new_sheet_name)
        else:
            ws = wb.create_sheet(title=new_sheet_name)

        flattened_data = []
        for course in data["course_completion"]:
            flattened_data.append({
                "Course Name": course["name"],
                "Completed": course["completed"],
                "Ongoing": course["ongoing"],
                "Percentage": course["percentage"]
            })

        df = pd.DataFrame(flattened_data)

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        add = 0
        for idx, course in enumerate(data["course_completion"], start=2): 
            chart = PieChart()
            labels = Reference(ws, min_col=2, min_row=1, max_col=3)
            data = Reference(ws, min_col=2, min_row=idx, max_col=3)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(labels)
            chart.title = course["name"]
        
            ws.add_chart(chart, f"F{idx + add}")
            add += 15

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
        return True, "Success"
    except:
        return False, "Could not generate the report."

def update_account_details(user_id, data):
    try:
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
        user.address = data['address']
        if user.user_type == 'student':
            student = Student.query.filter_by(user=user_id).first()
            student.tup_id = data['tup_id']
        db.session.commit()
        return True, "Account details have been changed."
    except Exception as e:
        return False, "An error occured while trying to update account."

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
    new_user = User(
        username=data['username'], 
        f_name=data['f_name'],
        m_name=data['m_name'],
        l_name=data['l_name'],
        ext_name=data['ext_name'],
        gender=data['gender'],
        password=data['password'],
        user_type=data['user_type'],
        email=data['email'],
        contact_no=data['contact_no'],
        civil_status=data['civil_status']
    )
    db.session.add(new_user)
    db.session.commit()
    if data['user_type'] == "admin":
        new_admin = Admin(user=new_user.id)
        db.session.add(new_admin)
    elif data['user_type'] == "instructor":
        new_instructor = Instructor(user=new_user.id)
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

def _remove_sa_instance_state(obj):
    if isinstance(obj, list):
        return [_remove_sa_instance_state(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _remove_sa_instance_state(value) for key, value in obj.items() if key != '_sa_instance_state'}
    else:
        return obj