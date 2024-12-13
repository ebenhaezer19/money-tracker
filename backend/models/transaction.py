from ..extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'Transaction'
    
    id_transaction = db.Column(db.String(64), primary_key=True)
    amount = db.Column(db.Numeric(10, 2))
    timestamp = db.Column(db.Date)
    description = db.Column(db.String(128))
    is_cancelled = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.String(64), db.ForeignKey('Category.id_category'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    category = db.relationship("Category", back_populates="transactions") 