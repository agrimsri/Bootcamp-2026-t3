from flask import Flask
from app.config import Config
from app.extensions import db



def create_app(class_name=Config):

    app = Flask(__name__)

    app.config.from_object(class_name)
    db.init_app(app)

    from app.models import User


    from app.routes.auth import auth
    from app.routes.views import views
    app.register_blueprint(auth)
    app.register_blueprint(views)

    return app