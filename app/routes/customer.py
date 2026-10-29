from datetime import datetime
from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from app.models import User, Professional, Customer, Service, ServiceRequest
from app.extensions import db

customer_bp = Blueprint('customer_bp', __name__, url_prefix='/customer')


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    requests = []
    if current_user.customer_profile:
        requests = ServiceRequest.query.filter_by(
            customer_id=current_user.customer_profile.id
        ).all()
    return render_template('/customer/dashboard.html', requests=requests)


@customer_bp.route('/services')
@login_required
def services():
    services = Service.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('/customer/services.html', services=services, today=today)


@customer_bp.route('/book-service', methods=['POST'])
@login_required
def book_service():
    if not current_user.customer_profile:
        flash("Only customers can book services.", "danger")
        return redirect(url_for('customer_bp.services'))

    service_id = request.form.get('service_id')
    date = request.form.get('date')
    time_slot = request.form.get('time_slot')

    if not service_id or not date or not time_slot:
        flash("Please fill in all booking details.", "danger")
        return redirect(url_for('customer_bp.services'))

    new_request = ServiceRequest(
        customer_id=current_user.customer_profile.id,
        service_id=int(service_id),
        date=date,
        time_slot=time_slot,
        status='requested'
    )
    db.session.add(new_request)
    db.session.commit()

    flash("Service requested successfully!", "success")
    return redirect(url_for('customer_bp.dashboard'))

