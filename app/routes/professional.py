from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from app.models import ServiceRequest, Professional
from app.extensions import db

professional_bp = Blueprint('professional_bp', __name__, url_prefix='/professional')


@professional_bp.route('/dashboard')
@login_required
def dashboard():
    prof = current_user.professional_profile
    if not prof:
        flash("Professional profile not found.", "danger")
        return redirect(url_for('views.home'))

    available_requests = []
    accepted_requests = []

    if prof.service_id:
        # Requests matching this professional's service that are waiting to be accepted
        available_requests = ServiceRequest.query.filter_by(
            service_id=prof.service_id,
            status='requested'
        ).all()

        # Requests already accepted by this professional
        accepted_requests = ServiceRequest.query.filter_by(
            professional_id=prof.id
        ).all()

    return render_template(
        '/professional/dashboard.html',
        available_requests=available_requests,
        accepted_requests=accepted_requests,
        professional=prof
    )


@professional_bp.route('/accept-request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    prof = current_user.professional_profile
    if not prof:
        flash("Only professionals can accept service requests.", "danger")
        return redirect(url_for('views.home'))

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for('professional_bp.dashboard'))

    # Ensure the request is still pending
    if service_request.status != 'requested':
        flash("This request is no longer available.", "warning")
        return redirect(url_for('professional_bp.dashboard'))

    # Assign this professional and mark as accepted
    service_request.professional_id = prof.id
    service_request.status = 'accepted'
    db.session.commit()

    flash(f"You have accepted the booking for {service_request.service.name}!", "success")
    return redirect(url_for('professional_bp.dashboard'))

