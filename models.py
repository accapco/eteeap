from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column('username', db.String(64), unique=True, nullable=False)
    f_name = db.Column('f_name', db.String(64))
    m_name = db.Column('m_name', db.String(64))
    l_name = db.Column('l_name', db.String(64))
    password = db.Column('password', db.String(64), nullable=False)
    user_type = db.Column(db.Enum('admin', 'instructor', 'student'), nullable=False)
    
class Admin(db.Model):
    __tablename__ = "admin"

    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'))

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column('title', db.String(64))
    code = db.Column('code', db.String(8))

class Class(db.Model):
    __tablename__ = "classes"

    id = db.Column("id", db.Integer, primary_key=True)
    course = db.Column(db.Integer, db.ForeignKey('courses.id'))
    units = db.Column("units", db.Integer)
    instructor = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    students = db.relationship('Student', secondary='enrollment', back_populates='classes')
    day = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

class Instructor(db.Model):
    __tablename__ = "instructors"

    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'))
    classes = db.relationship('Class', backref='classes')

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'))
    progress = db.Column(db.Enum('evaluation', 'enrollment', 'completion'), nullable=False, default='evaluation')
    instructors = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    classes = db.relationship('Class', secondary='enrollment', back_populates='students')

enrollment = db.Table(
  'enrollment',
  db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
  db.Column('course_id', db.Integer, db.ForeignKey('classes.id'))
)

class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column("user_id", db.Integer, db.ForeignKey('users.id'))
    filename = db.Column("filename", db.String(64), nullable=False)
    file = db.Column("file", db.LargeBinary, nullable=False)