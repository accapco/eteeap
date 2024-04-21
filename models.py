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
    password = db.Column("password", db.String(64), nullable=False)
    user_type = db.Column(db.Enum('admin', 'instructor', 'student'), nullable=False)
    
class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(64))
    code = db.Column("code", db.String(8))

class RequirementMaterial(db.Model):
    __tablename__ = "requirement_materials"

    id = db.Column("id", db.String(64), primary_key=True)
    filepath = db.Column("filepath", db.String(64))
    requirement = db.Column("requirement", db.Integer, db.ForeignKey('requirements.id'))

class RequirementSubmission(db.Model):
    __tablename__ = "requirement_submissions"

    id = db.Column("id", db.String(64), primary_key=True)
    filepath = db.Column("filepath", db.String(64))
    requirement = db.Column("requirement", db.Integer, db.ForeignKey('requirements.id'))

class Requirement(db.Model):
    __tablename__ = "requirements"

    id = db.Column("id", db.Integer, primary_key=True)
    enrollment = db.Column("enrollment", db.Integer, db.ForeignKey('enrollments.id'))
    title = db.Column("title", db.String(256))
    description = db.Column("description", db.String(256))
    materials = db.relationship("RequirementMaterial", backref='requirements_materials')
    submissions = db.relationship("RequirementSubmission", backref='requirements_submissions')
    progress = db.Column("progress", db.Enum('incomplete', 'evaluation', 'completed'), default='incomplete')

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column("id", db.Integer, primary_key=True)
    course = db.Column("course", db.Integer, db.ForeignKey('courses.id'))
    units = db.Column("units", db.Integer)
    instructor = db.Column("instructor", db.Integer, db.ForeignKey('instructors.id'))
    student = db.Column("student", db.Integer, db.ForeignKey('students.id'))
    status = db.Column("status", db.Enum('completed', 'ongoing', 'pending'), default='pending')
    requirements = db.relationship("Requirement", backref='enrollments')

class Instructor(db.Model):
    __tablename__ = "instructors"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))
    enrollments = db.relationship("Enrollment", backref='instructors')

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column("id", db.Integer, primary_key=True)
    user = db.Column("user", db.Integer, db.ForeignKey('users.id'))
    progress = db.Column(db.Enum('payment', 'evaluation', 'enrollment', 'completion'), nullable=False, default='payment')
    receipt_filepath = db.Column("receipt_filepath", db.String(64))
    document_filepath = db.Column("application_document_filepath", db.String(64))
    enrollments = db.relationship("Enrollment", backref='students')