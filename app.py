from flask import Flask, request, session, redirect, url_for, render_template

import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '.\\instance\\uploads'

from models import db, User, Admin

def create_default_user():
    existing_user = User.query.first()
    if not existing_user:
        default_user = User(username='admin', f_name="", m_name="", l_name="", password='12345', user_type='admin')
        db.session.add(default_user)
        default_admin = Admin(user_id=User.query.filter(User.username == "admin").one().id)
        db.session.add(default_admin)
        db.session.commit()

with app.app_context():
    db.create_all()
    create_default_user()

from views import views
app.register_blueprint(views, url_prefix='/index')

@app.route('/')
def _index():
    if 'user' in session:
        return redirect('/index/home')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = user.user_type
            session['id'] = user.id
            return redirect('/index/home')
        else:
            return render_template('login_template.html', message='Invalid username or password')
    return render_template('login_template.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('.login'))

@app.template_filter('filename')
def get_filename(filepath):
    return filepath.split('\\')[-1]

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)