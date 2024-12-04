from flask import Blueprint, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity
from connectors.db import Session
from models.transaction_models import order_detail

transactionBp = Blueprint('transactionBp',__name__)


@transactionBp.route('/transaction', methods=['GET'])
@jwt_required()
def transaction():
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

