from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from app.models import User, Professional, Customer, Service, ServiceRequest
from app.extensions import db

professional_bp = Blueprint('professional_bp', __name__,  url_prefix='/professional')


@professional_bp.route('/dashboard')
@login_required
def dashboard():
    prof = current_user.professional_profile
    available_requests = ServiceRequest.query.filter_by(service_id=prof.service_id, status='requested').all()
    accepted_requests = ServiceRequest.query.filter_by(professional_id=prof.id, status='accepted').all()
    completed_requests = ServiceRequest.query.filter_by(professional_id=prof.id, status='completed').all()
    return render_template('/professional/dashboard.html',
                            available_requests=available_requests,
                            professional=prof,
                            accepted_requests=accepted_requests,
                            completed_requests=completed_requests)


@professional_bp.route('/accept-request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    service_request = ServiceRequest.query.get(request_id)

    if service_request.status != 'requested':
        flash("This request is no longer available", 'warning')

    service_request.status = 'accepted'
    service_request.professional_id = current_user.professional_profile.id

    db.session.commit()

    flash("Request Accepted", 'success')
    return redirect(url_for('professional_bp.dashboard'))


@professional_bp.route('/profile')
def profile():
    return render_template('/professional/profile.html', prof=current_user.professional_profile)