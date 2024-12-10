from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from .. import db
from ..models import Transaction, Category
from ..utils import generate_id


transaction_bp = Blueprint('transaction', __name__)
    

@transaction_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """
    Get all transactions for the provided category and date range (defined by date_begin and date_end).
    """
    
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id"),
            "category_id": data.get("category_id"),
            "date_begin": data.get("date_begin"),
            "date_end": data.get("date_end")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Invalid category
        if not Category.query.filter_by(id_category=args["category_id"]).one_or_none():
            return jsonify({"message": "Invalid category."}), 400
        
        # Date range validity
        try:
            date_begin = datetime.strptime(args["date_begin"], f"%Y-%m-%d")
            date_end = datetime.strptime(args["date_end"], f"%Y-%m-%d")
            assert date_end >= date_begin
        except:
            date_end = datetime.now()
            date_begin = date_end - timedelta(weeks=1)
        
        # Query non-removed transactions for the given category
        # Sort by most recent
        transactions = Transaction.query.join(Category).filter(
            Category.user_id == current_user.id_user,
            Transaction.is_cancelled == False,
            Transaction.timestamp >= date_begin,
            Transaction.timestamp <= date_end
        ).order_by(Transaction.timestamp.desc()).all()
        
        if len(transactions) >= 1:
            return jsonify([{
                'id': t.id_transaction,
                'amount': int(t.amount),
                'timestamp': t.timestamp.isoformat(),
                'description': t.description
            } for t in transactions])

        # No category exists for the given user
        return (
            jsonify({"message": "No transactions exist for the given category."}), 200
        )
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@transaction_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id"),
            "category_id": data.get("category_id"),
            "amount": data.get("amount"),
            "timestamp": data.get("timestamp"),
            "description": data.get("description")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Invalid category
        if not Category.query.filter_by(id_category=args["category_id"]).one_or_none():
            return jsonify({"message": "Invalid category."}), 400
        
        # Invalid transaction amount
        try:
            args["amount"] = float(args["amount"])
            assert 0 < args["amount"] < 1_000_000_000_000_000
        except:
            return jsonify({
                "message": "Invalid transaction amount.",
                "details": "Transaction amount has to be between 0 and 1.000.000.000.000 IDR."
            }), 400
            
        # Invalid timestamp
        try:
            args['timestamp'] = datetime.strptime(args["timestamp"], f"%Y-%m-%d")
        except:
            return jsonify({"message": "Invalid timestamp."}), 400

        # Transaction stored
        transaction = Transaction(
            id_transaction = generate_id(),
            amount=args['amount'],
            timestamp=args['timestamp'],
            description=args['description'],
            category_id=args['category_id']
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({"message": "Transaction stored"}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@transaction_bp.route('/transactions', methods=['PATCH'])
@login_required
def edit_transaction():
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id"),
            "transaction_id": data.get("transaction_id"),
            "amount": data.get("amount"),
            "timestamp": data.get("timestamp"),
            "description": data.get("description")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Invalid transaction
        transaction = Transaction.query.filter_by(id_transaction=args["transaction_id"]).one_or_none()
        if not transaction:
            return jsonify({"message": "Invalid transaction."}), 400
        
        # Invalid transaction amount
        if args['amount']:
            try:
                args["amount"] = float(args["amount"])
                assert 0 < args["amount"] < 1_000_000_000_000_000
            except:
                return jsonify({
                    "message": "Invalid transaction amount.",
                    "details": "Transaction amount has to be between 0 and 1.000.000.000.000 IDR."
                }), 400
            
        # Invalid timestamp
        if args['timestamp']:
            try:
                args['timestamp'] = datetime.strptime(args["timestamp"], f"%Y-%m-%d")
            except:
                return jsonify({"message": "Invalid timestamp."}), 400

        # Transaction modified
        if args['amount']:
            transaction.amount = args['amount']
        if args['timestamp']:
            transaction.timestamp = args['timestamp']
        if args['description']:
            transaction.description = args['description']
        db.session.commit()
        
        return jsonify({"message": "Transaction modified"}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@transaction_bp.route('/transactions', methods=['DELETE'])
@login_required
def remove_transaction():
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id"),
            "transaction_id": data.get("transaction_id")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Invalid transaction
        transaction = Transaction.query.filter_by(id_transaction=args["transaction_id"]).one_or_none()
        if not transaction:
            return jsonify({"message": "Invalid transaction."}), 400

        # Transaction removed
        transaction.is_cancelled = True
        db.session.commit()
        
        return jsonify({"message": "Transaction removed"}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@transaction_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """
    Get all categories for the provided user.
    """
    
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Query categories for the given user
        categories = Category.query.filter_by(user_id=args["user_id"]) \
        .order_by(Category.title.asc()).all()
        
        if len(categories) >= 1:
            return jsonify([{
                'id': c.id_category,
                'title': c.title
            } for c in categories]), 200
        
        # No category exists for the given user
        return (
            jsonify({"message": "No category exists for the given user."}), 200
        )
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

@transaction_bp.route('/categories', methods=['PATCH'])
@login_required
def rename_category():
    try:
        data = request.get_json()
        
        args = {
            "user_id": data.get("user_id"),
            "category_id": data.get("category_id"),
            "title": data.get("title")
        }
        
        # Unable to authenticate user
        try:
            assert current_user.is_authenticated
            assert current_user.get_id() == args["user_id"]
        except:
            return jsonify({"message": "Unable to authenticate user."}), 401
        
        # Invalid category
        category_to_rename = Category.query.filter_by(id_category=args["category_id"]).one_or_none()
        if not category_to_rename:
            return jsonify({"message": "Invalid category."}), 400
        
        # Invalid title
        try:
            assert len(args["title"]) >= 1
        except:
            return jsonify({"message": "Invalid title."}), 400

        # Category renamed
        category_to_rename.title = args["title"]
        db.session.commit()
        
        return jsonify({"message": "Category renamed."}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    