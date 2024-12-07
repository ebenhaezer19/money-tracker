from flask_login import UserMixin

from . import db
from .utils import generate_id


class User(db.Model, UserMixin):
    id_user = db.Column(db.String(64), primary_key=True, default=generate_id())
    username = db.Column(db.String(64))
    password = db.Column(db.String(255))


class Transaction(db.Model):
    id_transaction = db.Column(db.String(64), primary_key=True, default=generate_id())
    amount = db.Column(db.Numeric(10, 2))
    timestamp = db.Column(db.DateTime)
    description = db.Column(db.String(128))
    is_cancelled = db.Column(db.Boolean, default=False)
    
    category = db.relationship("Category", backref="categories")
    

class Category(db.Model):
    id_category = db.Column(db.String(64), primary_key=True, default=generate_id())
    title = db.Column(db.String(64))
    
    user = db.relationship("User", backref="users")
