from flask_login import UserMixin
from ..extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    
    id_user = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(64))
    password = db.Column(db.String(255))
    
    def get_id(self):
        return self.id_user 