from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from .config import Config

login_manager = LoginManager()
db = SQLAlchemy()
cors = CORS()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    db.init_app(app)
    cors.init_app(app)

    from .auth.routes import auth_bp
    from .transaction.routes import transaction_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(transaction_bp, url_prefix="/transaction")

    login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "Unauthorized access"}, 401

    return app
