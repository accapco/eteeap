from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata=MetaData(naming_convention=naming_convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db, render_as_batch=True)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(64), unique=True, nullable=False)
    f_name = db.Column("f_name", db.String(64))
    m_name = db.Column("m_name", db.String(64))
    l_name = db.Column("l_name", db.String(64))
    ext_name = db.Column("ext_name", db.String(5))
    civil_status = db.Column("civil_status", db.Enum('Single', 'Married', 'Legally Separated', 'Widowed'))
    citizenship = db.Column("citizenship", db.String(20))
    birthyear = db.Column("birthyear", db.Integer)
    birthmonth = db.Column("birthmonth", db.Integer)
    birthday = db.Column("birthday", db.Integer)
    gender = db.Column("gender", db.Enum('M', 'F'))
    email = db.Column("email", db.String(64))
    contact_no = db.Column("contact_no", db.String(64))
    residency = db.Column("residency", db.Enum('local', 'foreign'), default='local')
    local_address = db.Column("local_address", db.String(100))
    foreign_address = db.Column("foreign_address", db.String(100))
    password = db.Column("password", db.String(64), nullable=False)
    user_type = db.Column(db.Enum('admin', 'instructor', 'student'), nullable=False)
    ft_login = db.Column("ft_login", db.Boolean, default=True)
    reset_password = db.Column("reset_password", db.Boolean, default=False)

class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))

class College(db.Model):
    __tablename__ = "colleges"

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    abbr = db.Column("abbr", db.String(10))
    programs = db.relationship("Program", backref=db.backref("college"))

class Program(db.Model):
    __tablename__ = "programs"

    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    abbr = db.Column("abbr", db.String(10))
    courses = db.relationship("Course", backref=db.backref("program"))
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"))

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(64))
    code = db.Column("code", db.String(8))
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"))

class RequirementMaterial(db.Model):
    __tablename__ = "requirement_materials"

    id = db.Column("id", db.Integer, primary_key=True)
    filepath = db.Column("filepath", db.String(64))
    filename = db.Column("filename", db.String(64))
    requirement = db.Column("requirement", db.Integer, db.ForeignKey('requirements.id'))

class RequirementSubmission(db.Model):
    __tablename__ = "requirement_submissions"

    id = db.Column("id", db.Integer, primary_key=True)
    filepath = db.Column("filepath", db.String(64))
    filename = db.Column("filename", db.String(64))
    requirement = db.Column("requirement", db.Integer, db.ForeignKey('requirements.id'))

class Requirement(db.Model):
    __tablename__ = "requirements"

    id = db.Column("id", db.Integer, primary_key=True)
    enrollment = db.Column("enrollment", db.Integer, db.ForeignKey('enrollments.id'))
    title = db.Column("title", db.String(256))
    description = db.Column("description", db.Text)
    materials = db.relationship("RequirementMaterial", backref='requirements_materials')
    submissions = db.relationship("RequirementSubmission", backref='requirements_submissions')
    progress = db.Column("progress", db.Enum('incomplete', 'evaluation', 'completed'), default='incomplete')

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column("id", db.Integer, primary_key=True)
    course = db.Column("course", db.Integer, db.ForeignKey('courses.id'))
    units = db.Column("units", db.Integer)
    ay = db.Column("academic_year", db.String(9))
    semester = db.Column("semester", db.Enum('1st', '2nd', 'Midyear'))
    instructor = db.Column("instructor", db.Integer, db.ForeignKey('instructors.id'))
    student = db.Column("student", db.Integer, db.ForeignKey('students.id'))
    status = db.Column("status", db.Enum('listed', 'pending', 'ongoing', 'completed'), default='listed')
    grade = db.Column("grade", db.Float)
    form1 = db.Column("form1path", db.String(64))
    form2 = db.Column("form2path", db.String(64))
    form3 = db.Column("form3path", db.String(64))
    honorarium = db.Column("honorarium", db.Enum('onprocess', 'released'), default='onprocess')
    requirements = db.relationship("Requirement", backref='enrollments')

class Instructor(db.Model):
    __tablename__ = "instructors"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))
    college = db.Column(db.Integer, db.ForeignKey("colleges.id"))
    enrollments = db.relationship("Enrollment", backref='instructors')

class EducationalBackground(db.Model):
    __tablename__ = "educational_backgrounds"

    id = db.Column("id", db.Integer, primary_key=True)
    school = db.Column("school", db.String(64))
    degree = db.Column("degree", db.String(64))
    start_year = db.Column("start_year", db.Integer())
    end_year = db.Column("end_year", db.Integer())
    academic_honors = db.Column("academic_honors", db.Integer())
    instructor = db.Column("instructor", db.Integer, db.ForeignKey('instructors.id'))

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))
    progress = db.Column(db.Enum('payment', 'enrollment', 'enrolled', 'graduate'), nullable=False, default='payment')
    program = db.Column("program", db.Integer, db.ForeignKey('programs.id'))
    ay = db.Column("academic_year", db.String(9))
    tup_id = db.Column("tup_id", db.String(20))
    semester = db.Column("semester", db.Enum('1st', '2nd', 'Midyear'))
    receipt_filepath = db.Column("receipt_filepath", db.String(64))
    enrollments = db.relationship("Enrollment", backref='students')