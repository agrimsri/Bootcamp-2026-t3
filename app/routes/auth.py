from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import User, Customer, Professional, Service
from flask_login import login_user, logout_user
from app.extensions import db
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', "").strip().lower()
        password = request.form.get('password', "").strip()

        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('/auth/login.html')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exist. Please sign up.", "danger")
            return redirect(url_for('views.home'))

        if not user.is_active:
            flash("Account has been suspended", 'danger')
            redirect(url_for('views.home'))

        if user.role == 'professional' and user.professional_profile.approved == False:
            flash("Your account is pending approval. Please wait for admin approval.", "info")
            return redirect(url_for('views.home'))


        if user.check_password(password):
            login_user(user)
            role = user.role
            flash("Login successful!", "success")
            if role == 'customer':
                return redirect(url_for('views.customer_dashboard'))
            elif role == 'professional':
                return redirect(url_for('views.professional_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_bp.admin_dashboard'))
            else:
                flash("Unknown user role.", "danger")
                return redirect(url_for('views.home'))
        else:
            flash("Incorrect password.", "danger")
            return redirect(url_for('auth.login'))

    return render_template('/auth/login.html') 

@auth.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        email = request.form.get('email', "").strip().lower()
        password = request.form.get('password', "").strip()

        username = request.form.get('username', "").strip()
        address = request.form.get('address', "").strip()

        user = User.query.filter_by(email=email).first()
        if user:
            flash("User already exists. Please log in.", "danger")
            return redirect(url_for('auth.login'))

        user = User(email=email, role='customer', username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        cust = Customer(user_id=user.id, address=address)
        db.session.add(cust)
        db.session.commit()

        flash("Registration successful!" , "success")
        return redirect(url_for('views.customer_dashboard'))

    return render_template('/auth/register_customer.html')

@auth.route('/register/professional', methods=['GET', 'POST'])
def register_professional():
    if request.method == 'POST':
        email = request.form.get('email', "").strip().lower()
        password = request.form.get('password', "").strip()

        username = request.form.get('username', "").strip()
        service_id = request.form.get('service', "").strip()
        about = request.form.get('about', "").strip()

        user = User.query.filter_by(email=email).first()
        if user:
            flash("User already exists. Please log in.", "danger")
            return redirect(url_for('auth.login'))

        user = User(email=email, role='professional', username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        prof = Professional(user_id=user.id, service_id=service_id, about=about)
        db.session.add(prof)
        db.session.commit()

        flash("Registration successful! Please wait for admin approval." , "info")
        return redirect(url_for('views.home'))

    services = db.session.query(Service).all()  # Fetch all services from the database
    return render_template('/auth/register_professional.html', services=services)

@auth.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('views.home'))


