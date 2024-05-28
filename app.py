from flask import Flask, request, session, redirect, url_for, render_template, flash, g

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
        default_user = User(username='admin', f_name="", m_name="", l_name="", password='12345', user_type='admin', ft_login=True)
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

from forms import LoginForm, FTLoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = user.user_type
            session['id'] = user.id
            if user.ft_login:
                return redirect(url_for('ft_login', user_type=session['user']))
            return redirect('/index/home')
        else:
            flash("Incorrect login details.", 'error')
    return render_template('login_template.html', form=form)

from db_functions import complete_ft_login

@app.route('/first_time_login/<user_type>', methods=['GET', 'POST'])
def ft_login(user_type):
    g.user = None
    if 'user' in session:
        g.user = session['user']
    else:
        return redirect('/login')
    form = FTLoginForm(user_type)
    if form.validate_on_submit():
        success, message = complete_ft_login(session.get('id'), form.data)
        if success:
            return redirect('/index/home')
        else:
            flash(message, 'error')
    else:
        if form.password_confirm.errors:
            for error in form.password_confirm.errors:
                flash(error, 'error')
    return render_template('ft-login.html', user_type=user_type, form=form)

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