from flask import Blueprint, render_template
from app.models import Professional

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

@views.route('/admin/dashboard')
def admin_dashboard():
    return render_template('/admin/dashboard.html')


@views.route('/admin/professionals')
def admin_professionals():
    professionals = Professional.query.all()
    return render_template('/admin/professionals.html', professionals=professionals)