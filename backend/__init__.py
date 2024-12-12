from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from backend.config import Config


bcrypt = Bcrypt()
login_manager = LoginManager()
db = SQLAlchemy()
cors = CORS()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['DEBUG'] = True

    bcrypt.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)
    cors.init_app(app, supports_credentials=True)

    @app.route('/test-db')
    def test_db():
        try:
            db.session.execute(text('SELECT 1'))
            return {"message": "Koneksi database berhasil!"}, 200
        except Exception as e:
            return {"error": f"Koneksi database gagal: {str(e)}"}, 500

    from backend.auth.routes import auth_bp
    from backend.transaction.routes import transaction_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(transaction_bp, url_prefix="/api")

    # login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "Unauthorized access"}, 401

    return app
