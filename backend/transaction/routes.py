from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from .. import db  
from models import Transaction, Category

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('transactions', methods=['GET'])
@login_required
def get_transactions():
    try:
        transactions = Transaction.query.join(Category).filter(
            Category.user_id == current_user.id_user,
            Transaction.is_cancelled == False
        ).all()
        
        return jsonify([{
            'id': t.id_transaction,
            'amount': float(t.amount),
            'timestamp': t.timestamp.isoformat(),
            'description': t.description,
            'category': {
                'id': t.category.id_category,
                'title': t.category.title
            }
        } for t in transactions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('transactions', methods=['POST'])
@login_required
def create_transaction():
    try:
        data = request.get_json()
        category = Category.query.get(data['id_category'])
        
        if not category or category.user_id != current_user.id_user:
            return jsonify({'error': 'Invalid category'}), 400

        transaction = Transaction(
            amount=data['amount'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data['description'],
            category_id=data['id_category']
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'id': transaction.id_transaction,
            'amount': float(transaction.amount),
            'timestamp': transaction.timestamp.isoformat(),
            'description': transaction.description,
            'category': {
                'id': transaction.category.id_category,
                'title': transaction.category.title
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('transactions/<id_transaction>', methods=['DELETE'])
@login_required
def delete_transaction(id_transaction):
    try:
        transaction = Transaction.query.get_or_404(id_transaction)
        if transaction.category.user_id != current_user.id_user:
            return jsonify({'error': 'Unauthorized'}), 403

        transaction.is_cancelled = True
        db.session.commit()
        return '', 204
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
