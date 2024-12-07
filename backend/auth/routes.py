import re
import requests

from flask import (
    Blueprint,
    jsonify,
    request,
    session,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from .config import Config
from .. import bcrypt, db, login_manager
from ..models import User


auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Allows the IT team to register a user account; this feature is not to be enabled in production.
    """
    
    data = request.get_json()
    
    username = data.get("username")
    password = data.get("password")
    
    # Incomplete request parameters
    if not username or not password:
        return (
            jsonify({
            "message": "Incomplete request parameters.",
            "details": "Missing username or password."}), 400
        )
    
    # The username provided is already taken
    if User.query.filter_by(username=username).one_or_none():
        return (
            jsonify({
            "message": "The username provided is already taken.",
            "details": "Please choose a different username."}), 409
        )
        
    # Invalid username
    if not re.match(Config.USERNAME_REGEX, username):
        return (
            jsonify({
            "message": "Invalid username.",
            "details": "Username can only contain alphanumeric characters, underscores, and hyphens."}), 400
        )
    
    # Registration successful
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user_to_register = User(username=username, password=password_hash)
    db.session.add(user_to_register)
    db.session.commit()
    
    return (
        jsonify({"message": "Registration successful."}), 201
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Allows users to login to their account.
    """
    
    data = request.get_json()
    
    username = data.get("username")
    password = data.get("password")
    
    # Incomplete request parameters
    if not username or not password:
        return (
            jsonify({
            "message": "Incomplete request parameters.",
            "details": "Missing username or password."}), 400
        )
    
    # Query the user by username
    user = User.query.filter_by(username=username).one_or_none()
    
    # Invalid username or password
    try:
        assert user  # invalid username
        assert bcrypt.check_password_hash(user.password, password)  # invalid password
    except:
        return jsonify({"message": "Invalid username or password."}), 401
    
    # Login successful
    login_user()
    return (
        jsonify({"message": "Login successful."}), 200
    )
    
    
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return (
        jsonify({"message": "Logout successful."}), 200
    )
