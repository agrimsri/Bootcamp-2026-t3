from flask import Blueprint, render_template, redirect, url_for, request
from app.models import User
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return render_template('/auth/login.html', message="Login successful!")

    return render_template('/auth/login.html') 

@auth.route('/register/customer')
def register_customer():
    return render_template('/auth/register_customer.html')

@auth.route('/register/professional')
def register_professional():
    return render_template('/auth/register_professional.html')

@auth.route('/logout')
def logout():
    return redirect(url_for('views.home'))