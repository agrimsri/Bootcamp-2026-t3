from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required
from app.models import User, Professional, Customer, Service
from app.extensions import db

customer_bp = Blueprint('customer_bp', __name__,  url_prefix='/customer')


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('/customer/dashboard.html')


@customer_bp.route('/services')
@login_required
def services():
    services = Service.query.all()

    return render_template('/customer/services.html', services=services)


# @customer_bp.route('customer/book-service', methods=['POST'])
# def book_service():
