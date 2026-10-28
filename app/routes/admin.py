from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required
from app.models import User, Professional, Customer, Service
from app.extensions import db

admin_bp = Blueprint('admin_bp', __name__,  url_prefix='/admin')


@admin_bp.route('/dashboard')
def admin_dashboard():
    return render_template('/admin/dashboard.html')


@admin_bp.route('/professionals')
@login_required
def admin_professionals():
    pending_professionals = Professional.query.filter_by(approved=False).all()
    approved_professionals = Professional.query.filter_by(approved=True).all()
    return render_template('/admin/professionals.html', pending_professionals=pending_professionals, approved_professionals=approved_professionals)

@admin_bp.route('/professionals/approve/<int:professional_id>', methods=['POST'])
@login_required
def approve_professional(professional_id):
    professional = Professional.query.get(professional_id)
    if professional:
        professional.approved = True
        db.session.commit()
        flash(f"Professional {professional.user.username} has been approved.", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for('admin_bp.admin_professionals'))

@admin_bp.route('/professionals/reject/<int:professional_id>', methods=['POST'])
@login_required
def reject_professional(professional_id):
    professional = Professional.query.get(professional_id)
    if professional:
        professional.approved = False
        db.session.commit()
        flash(f"Professional {professional.user.username} has been rejected.", "success")
    else:
        flash("Professional not found.", "danger")
    return redirect(url_for('admin_bp.admin_professionals'))

@admin_bp.route('/blacklist/<int:professional_id>', methods=['POST'])
@login_required
def toggle_blacklist_professional(professional_id):
    proffesional = Professional.query.get(professional_id)
    proffesional.user.is_active = not (proffesional.user.is_active)
    db.session.commit()
    flash('Status updated', "success")
    return redirect(url_for('admin_bp.admin_professionals'))

@admin_bp.route('/services')
@login_required
def services():
    services = Service.query.all()
    return render_template('/admin/services.html', services=services)

@admin_bp.route('/services/create', methods=['POST'])
@login_required
def add_service():
    name = request.form.get('name', '')
    description = request.form.get('description', '')
    price = request.form.get('price', 0)

    service = Service(name=name, description=description, price=price)
    db.session.add(service)
    db.session.commit()

    flash('Service created', 'success')
    return redirect(url_for('admin_bp.services'))

@admin_bp.route('/services/delete/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    service = Service.query.get(service_id)

    db.session.delete(service)
    db.session.commit()

    flash('Service deleted', 'success')
    return redirect(url_for('admin_bp.services'))

@admin_bp.route('/services/edit/<int:service_id>', methods=['POST'])
@login_required
def edit_service(service_id):

    service = Service.query.get(service_id)

    name = request.form.get('name', service.name)
    description = request.form.get('description', service.description)
    price = request.form.get('price', service.price)

    service.name = name
    service.description = description
    service.price = price

    db.session.commit()

    flash('Service edited', 'success')
    return redirect(url_for('admin_bp.services'))
