from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user,  login_required
from models import User

login_bp = Blueprint("login", __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home.home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))