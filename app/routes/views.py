from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.models import Professional, User
from flask_login import login_required
from app.extensions import db

views = Blueprint('views', __name__)

@views.route('/')
@views.route('/home')
def home():
    user = 'Arjun'
    age = 32
    return render_template('home.html', user=user, age=age)

@views.route('/customer/dashboard')
def customer_dashboard():
    return render_template('/customer/dashboard.html')

@views.route('/professional/dashboard')
def professional_dashboard():
    return render_template('/professional/dashboard.html')



##############################
# ADMIN ROUTES
##############################


##############################
