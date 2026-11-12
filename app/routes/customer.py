from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from app.models import User, Professional, Customer, Service, ServiceRequest
from app.extensions import db

customer_bp = Blueprint('customer_bp', __name__,  url_prefix='/customer')


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    ongoing_service_requests = ServiceRequest.query.filter_by(customer_id=current_user.customer_profile.id, status='accepted').all()
    completed_service_requests = ServiceRequest.query.filter_by(customer_id=current_user.customer_profile.id, status='completed').all()

    return render_template('/customer/dashboard.html', ongoing_service_requests=ongoing_service_requests, completed_service_requests=completed_service_requests)


@customer_bp.route('/services')
@login_required
def services():
    services = Service.query.all()

    return render_template('/customer/services.html', services=services)


@customer_bp.route('customer/book-service', methods=['POST'])
@login_required
def book_service():
    service_id = request.form.get('service_id')
    date = request.form.get('date')
    time_slot = request.form.get('time_slot')

    new_request = ServiceRequest(
        customer_id=current_user.customer_profile.id,
        service_id=service_id,
        date=date,
        time_slot=time_slot
    )

    db.session.add(new_request)
    db.session.commit()

    flash("Service request created", 'success')
    return redirect(url_for('customer_bp.dashboard'))

@customer_bp.route('customer/request/completed/<int:request_id>', methods=['POST'])
@login_required
def request_completed(request_id):
    service_request = ServiceRequest.query.get(request_id)
    service_request.status = "completed"
    db.session.commit()

    flash("Service request completed", 'success')
    return redirect(url_for('customer_bp.dashboard'))
