from flask import Flask, request, jsonify
from flask_login import current_user, login_user

from .config import Config
from .extensions import db, bcrypt, login_manager, cors
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Configure CORS
    cors.init_app(app, 
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True
            }
        },
        supports_credentials=True
    )

    @app.before_request
    def check_auth():
        # Skip untuk endpoint yang tidak memerlukan auth
        if request.path == '/api/auth/login' or \
           request.path == '/test-db' or \
           request.method == 'OPTIONS':
            return None

        # Check auth untuk endpoint API
        if request.path.startswith('/api/'):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "No auth token"}), 401
            
            token = auth_header.split(' ')[1]
            user = User.query.filter_by(id_user=token).first()
            
            if not user:
                return jsonify({"error": "Invalid token"}), 401
                
            login_user(user)

    # Register blueprints
    from .auth.routes import auth_bp
    from .transaction.routes import transaction_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(transaction_bp, url_prefix="/api")

    @login_manager.unauthorized_handler
    def unauthorized():
        return {"error": "Unauthorized access"}, 401

    return app
