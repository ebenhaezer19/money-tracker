from flask_login import UserMixin
from .extensions import db


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    
    id_user = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(255))
    
    def get_id(self):
        return self.id_user


class Category(db.Model):
    __tablename__ = 'Category'
    
    id_category = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(64))
    user_id = db.Column(db.String(64), db.ForeignKey('User.id_user'))
    user = db.relationship("User", backref="categories")


class Transaction(db.Model):
    __tablename__ = 'Transaction'
    
    id_transaction = db.Column(db.String(64), primary_key=True)
    amount = db.Column(db.Numeric(10, 2))
    timestamp = db.Column(db.Date)
    description = db.Column(db.String(128))
    is_cancelled = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.String(64), db.ForeignKey('Category.id_category'))
    category = db.relationship("Category", backref="transactions")
