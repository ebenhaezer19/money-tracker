from flask import Flask, request, jsonify
from flask_login import current_user, login_user
from flask_cors import CORS

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
    
    # Konfigurasi CORS yang lebih permisif untuk development
    CORS(app, 
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"],  # Frontend URL
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "send_wildcard": False,
                "max_age": 86400  # Cache preflight request selama 24 jam
            }
        },
        supports_credentials=True
    )

    # Handle OPTIONS request
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 200

    @app.before_request
    def check_auth():
        # Skip untuk endpoint yang tidak memerlukan auth
        if request.path == '/api/auth/login' or \
           request.path == '/test-db' or \
           request.method == 'OPTIONS':  # Skip auth check untuk OPTIONS request
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

    # Tambahkan error handler untuk CORS
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    return app
