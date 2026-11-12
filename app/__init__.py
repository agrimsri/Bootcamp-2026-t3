from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from flask import current_app

from app.models import User


def seed_admin():
    admin_email = current_app.config.get('ADMIN_EMAIL')
    admin_password = current_app.config.get('ADMIN_PASSWORD')

    admin_user = User.query.filter_by(email=admin_email).first()
    
    if admin_user:
        return  # Admin user already exists

    admin_user = User(email=admin_email, role='admin', username='Admin')
    admin_user.set_password(admin_password)

    db.session.add(admin_user)
    db.session.commit()

def seed_services():
    from app.models import Service

    services = [
        {"name": "Plumbing", "description": "All plumbing related services.", "price": 50.0},
        {"name": "Electrical", "description": "Electrical installation and repair.", "price": 60.0},
        {"name": "Cleaning", "description": "Home and office cleaning services.", "price": 30.0},
        {"name": "Carpentry", "description": "Woodwork and furniture repair.", "price": 70.0},
        {"name": "Painting", "description": "Interior and exterior painting services.", "price": 40.0},
    ]

    for service_data in services:
        service = Service.query.filter_by(name=service_data["name"]).first()
        if not service:
            new_service = Service(
                name=service_data["name"],
                description=service_data["description"],
                price=service_data["price"]
            )
            db.session.add(new_service)

    db.session.commit()

def create_app(class_name=Config):

    app = Flask(__name__)

    app.config.from_object(class_name)
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Reload a logged-in user from the id stored in the session cookie."""
        return db.session.get(User, int(user_id))


    from app.routes.auth import auth
    from app.routes.views import views
    from app.routes.admin import admin_bp
    from app.routes.customer import customer_bp
    from app.routes.professional import professional_bp
    app.register_blueprint(auth)
    app.register_blueprint(views)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(professional_bp)

    return app