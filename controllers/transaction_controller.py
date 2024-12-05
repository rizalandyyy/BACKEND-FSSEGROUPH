from flask import Blueprint, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import Session
from models.transaction_models import order_detail
from models.user_models.user import User
from models.transaction_models import order_product

transactionBp = Blueprint('transactionBp',__name__)


@transactionBp.route('/transaction', methods=['GET'])
@jwt_required()
def transaction():
    # try:
        current_user = get_jwt_identity()
        with Session() as session:
            transaction_detail = session.query(order_detail).filter_by(user_id=current_user['id']).first()
            print (transaction_detail)
            # order_items = session.query(order_product).filter_by(order_id=transaction_detail.id).all()
            # list_transaction = [
            #     {
            #         'id': transaction_detail.id,
            #         ''
            #     }
            # ]
                    
        return jsonify({
            'success' : True,
            'message': 'Transaction retrieved successfully'}), 200
    
@transactionBp.route('/transaction', methods=['GET'])
@jwt_required()
def transaction_history():
    current_user = get_jwt_identity()
    
    with Session() as session:
        try:
            transactions = session.query(order_detail).filter_by(user_id=current_user['id']).all()
            if not transactions:
                return jsonify({
                    'success' : False,
                    'message': 'Transaction not found'}), 404
            return jsonify({
                'success' : True,
                'message': 'Transaction retrieved successfully',
                'data': transactions}), 200
        except Exception as e:
            return jsonify({
                'success' : False,
                'message': 'Error retrieving transaction',
                'data': {'error': str(e)}}), 500

