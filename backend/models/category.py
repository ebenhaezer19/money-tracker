from ..extensions import db

class Category(db.Model):
    __tablename__ = 'Category'
    
    id_category = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(64))
    user_id = db.Column(db.String(64), db.ForeignKey('User.id_user'))
    color = db.Column(db.String(7), default='#4CAF50')
    
    # Relationships
    user = db.relationship("User", backref="categories")
    transactions = db.relationship("Transaction", back_populates="category") 