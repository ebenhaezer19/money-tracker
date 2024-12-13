from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import pytz  # Tambahkan import ini

from ..extensions import db
from ..models import Transaction, Category
from ..utils import generate_id

transaction_bp = Blueprint('transaction', __name__)

# Definisikan timezone Jakarta
jakarta_tz = pytz.timezone('Asia/Jakarta')

@transaction_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def handle_categories():
    if request.method == 'GET':
        """Get all categories for current user"""
        try:
            categories = Category.query.filter_by(user_id=current_user.id_user).all()
            
            if not categories:
                return jsonify([]), 200
                
            return jsonify([{
                'id': category.id_category,
                'name': category.title,
                'budget': 1000000,  # Default budget
                'color': category.color
            } for category in categories]), 200
            
        except Exception as e:
            print(f"Error getting categories: {str(e)}")
            return jsonify({'error': str(e)}), 500
            
    elif request.method == 'POST':
        """Create new category"""
        try:
            data = request.get_json()
            
            # Validasi input
            if not data.get('name'):
                return jsonify({'error': 'Category name is required'}), 400
                
            # Generate random color jika tidak ada
            if not data.get('color'):
                colors = ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0', '#F44336']
                data['color'] = colors[len(Category.query.filter_by(user_id=current_user.id_user).all()) % len(colors)]
            
            # Buat kategori baru
            new_category = Category(
                id_category=generate_id(),
                title=data['name'],
                user_id=current_user.id_user,
                color=data['color']
            )
            
            db.session.add(new_category)
            db.session.commit()
            
            return jsonify({
                'id': new_category.id_category,
                'name': new_category.title,
                'budget': 1000000,  # Default budget
                'color': new_category.color
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating category: {str(e)}")
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

            print(f"Fetching transactions from {start_date} to {end_date}")

            # Convert string dates to datetime objects for comparison
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Add one day to end_date to include transactions on the end date
            end_date = end_date + timedelta(days=1)

            # Query transactions
            transactions = Transaction.query\
                .join(Category)\
                .filter(
                    Category.user_id == current_user.id_user,
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp < end_date,  # Changed to < end_date
                    Transaction.is_cancelled == False
                )\
                .order_by(Transaction.timestamp.desc())\
                .all()

            result = [{
                'id': t.id_transaction,
                'amount': float(t.amount),
                'date': t.timestamp.strftime('%Y-%m-%d'),
                'description': t.description,
                'category': t.category_id,
                'created_at': t.created_at.astimezone(jakarta_tz).strftime('%Y-%m-%d %H:%M:%S') if t.created_at else None
            } for t in transactions]

            print(f"Found {len(result)} transactions")
            return jsonify(result), 200

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
            
            # Set created_at dengan waktu Jakarta
            new_transaction.created_at = datetime.now(jakarta_tz)
            
            db.session.add(new_transaction)
            db.session.commit()
            
            return jsonify({
                'id': new_transaction.id_transaction,
                'amount': float(new_transaction.amount),
                'date': new_transaction.timestamp.strftime('%Y-%m-%d'),
                'description': new_transaction.description,
                'category': new_transaction.category_id,
                'created_at': new_transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
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

@transaction_bp.route('/categories/<category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    try:
        category = Category.query.filter_by(
            id_category=category_id,
            user_id=current_user.id_user
        ).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
            
        data = request.get_json()
        
        if 'color' in data:
            # Validasi format warna
            if not data['color'].startswith('#') or len(data['color']) != 7:
                return jsonify({'error': 'Invalid color format'}), 400
            category.color = data['color']
            
        if 'name' in data:
            # Validasi nama kategori
            if not data['name'].strip():
                return jsonify({'error': 'Category name cannot be empty'}), 400
            category.title = data['name'].strip()
            
        db.session.commit()
        
        return jsonify({
            'id': category.id_category,
            'name': category.title,
            'color': category.color
        })
        
    except Exception as e:
        db.session.rollback()
        print('Error updating category:', str(e))
        return jsonify({'error': 'Failed to update category'}), 500

@transaction_bp.route('/categories/<category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    try:
        # Cari kategori
        category = Category.query.filter_by(
            id_category=category_id,
            user_id=current_user.id_user
        ).first()
        
        if not category:
            return jsonify({'error': 'Category not found'}), 404
            
        # Hapus semua transaksi terkait
        Transaction.query.filter_by(category_id=category_id).delete()
        
        # Hapus kategori
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Category deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print('Error deleting category:', str(e))
        return jsonify({'error': 'Failed to delete category'}), 500
    