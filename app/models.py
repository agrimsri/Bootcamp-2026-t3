from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    # Relationships
    customer_profile = db.relationship('Customer', back_populates='user', uselist=False)
    professional_profile = db.relationship('Professional', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='customer_profile')


class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    about = db.Column(db.String(500), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='professional_profile')
    service = db.relationship('Service', back_populates='professionals')


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    professionals = db.relationship('Professional', back_populates='service')