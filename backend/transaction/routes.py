from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Transaction, Category
from ..utils import generate_id

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """Get all categories for current user"""
    try:
        # Get categories for current user
        categories = Category.query.filter_by(user_id=current_user.id_user).all()
        
        if not categories:
            return jsonify([]), 200
            
        return jsonify([{
            'id': category.id_category,
            'name': category.title,
            'budget': 1000000,  # Default budget
            'color': get_category_color(category.id_category)
        } for category in categories]), 200
        
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions', methods=['GET', 'POST'])
@login_required
def handle_transactions():
    if request.method == 'GET':
        try:
            # Get date range from query params
            start_date = request.args.get('date_begin', 
                (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            end_date = request.args.get('date_end', 
                datetime.now().strftime('%Y-%m-%d'))

            # Query transactions
            transactions = Transaction.query\
                .join(Category)\
                .filter(
                    Category.user_id == current_user.id_user,
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date,
                    Transaction.is_cancelled == False
                )\
                .order_by(Transaction.timestamp.desc())\
                .all()

            return jsonify([{
                'id': t.id_transaction,
                'amount': float(t.amount),
                'date': t.timestamp.strftime('%Y-%m-%d'),
                'description': t.description,
                'category': t.category_id
            } for t in transactions]), 200

        except Exception as e:
            print(f"Error getting transactions: {str(e)}")
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            print("Received transaction data:", data)

            # Validate category
            category = Category.query.filter_by(
                id_category=data['category'],
                user_id=current_user.id_user
            ).first()
            
            if not category:
                return jsonify({'error': 'Invalid category'}), 400

            # Create transaction
            new_transaction = Transaction(
                id_transaction=generate_id(),
                amount=float(data['amount']),
                timestamp=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                description=data.get('description', ''),
                category_id=data['category']
            )
            
            db.session.add(new_transaction)
            db.session.commit()
            
            return jsonify({
                'id': new_transaction.id_transaction,
                'amount': float(new_transaction.amount),
                'date': new_transaction.timestamp.strftime('%Y-%m-%d'),
                'description': new_transaction.description,
                'category': new_transaction.category_id
            }), 201
            
        except Exception as e:
            print(f"Error creating transaction: {str(e)}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transactions/<transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    try:
        # Cari transaksi berdasarkan ID dan user
        transaction = Transaction.query.filter_by(
            id_transaction=transaction_id
        ).join(Category).filter(
            Category.user_id == current_user.id_user
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
            
        data = request.get_json()
        print("Updating transaction:", transaction_id, "with data:", data)
        
        # Validate category if being updated
        if 'category' in data:
            category = Category.query.filter_by(
                id_category=data['category'],
                user_id=current_user.id_user
            ).first()
            if not category:
                return jsonify({'error': 'Invalid category'}), 400
            transaction.category_id = data['category']
            
        # Update fields
        if 'date' in data:
            transaction.timestamp = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'description' in data:
            transaction.description = data['description']
            
        db.session.commit()
        
        # Return updated data
        return jsonify({
            'id': transaction.id_transaction,
            'amount': float(transaction.amount),
            'date': transaction.timestamp.strftime('%Y-%m-%d'),
            'description': transaction.description,
            'category': transaction.category_id
        })
        
    except Exception as e:
        db.session.rollback()
        print('Error updating transaction:', str(e))
        return jsonify({'error': 'Failed to update transaction'}), 500

@transaction_bp.route('/transactions/<transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        transaction = Transaction.query.filter_by(
            id_transaction=transaction_id
        ).join(Category).filter(
            Category.user_id == current_user.id_user
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
            
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print('Error deleting transaction:', str(e))
        return jsonify({'error': 'Failed to delete transaction'}), 500

def get_category_color(category_id):
    """Get consistent color for category"""
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#F44336']
    index = hash(category_id) % len(colors)
    return colors[index]
    