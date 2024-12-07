from flask import Blueprint, jsonify, request
from connectors.db import Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models.cart import Cart
from models.transaction_models.order_product import OrderProduct
from models.transaction_models.order_detail import OrderDetail
from models.user_models.user import User


cartBp = Blueprint('cartBp',__name__)

@cartBp.route('/cart', methods=['GET'])
@jwt_required()
def cart():
    current_user = get_jwt_identity()
    with Session() as session : 
        try:
            user = session.query(User).filter_by(id= id , userName = current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            cart = session.query(Cart).filter_by(user_id=user.id).all()
            if not cart:
                return jsonify({
                    'success' : False,
                    'message': 'Cart is Empty'
                }), 404
            return jsonify({
                'success' : True,
                'message': 'Cart retrieved successfully',
                'data': cart
            }), 200
        except Exception as e:
            return jsonify({
                'success' : False,
                'message': 'Error retrieving cart'}), 400
                
    
    
@cartBp.route('/cart', methods=['POST'])
@jwt_required()
def addcart():
    data = request.get_json()
    if data is None:
        return jsonify({
            'success' : False,
            'message' : 'cart is empty'
        }), 400
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            cart = Cart(user_id=user.id, product_id=data['product_id'], quantity=data['quantity'])
            session.add(cart)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Product added to cart successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success' : False,
                'message' : 'Error adding product to cart',
                'data': {'error': str(e)}
            })
    
@cartBp.route('/cart/<int:product_id>', methods=['DELETE'])
@jwt_required()
def deleteitemsincart(product_id):
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(id= id, userName= current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            cart = session.query(Cart).filter_by(user_id=user.id, product_id=product_id).first()
            if not cart:
                return jsonify({
                    'success' : False,
                    'message': 'Cart is empty'
                }), 404
            session.delete(cart)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Product deleted from cart successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success' : False,
                'message' : 'Error deleting product from cart',
                'data': {'error': str(e)}
            })

            
            
@cartBp.route('/cart/<int:product_id>', methods=['PUT'])
@jwt_required()
def updatecart(product_id):
    data = request.get_json()
    if data is None:
        return jsonify({
            'success' : False,
            'message' : 'no data'
        }), 400
    current_user = get_jwt_identity()
    with Session() as session :
        try:
            user = session.query(User).filter_by(id= id, userName = current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            cart = session.query(Cart).filter_by(user_id=user.id, product_id=product_id).first()
            if not cart:
                return jsonify({
                    'success' : False,
                    'message': 'Cart not found'
                }), 404
            for key, value in data.items():
                if hasattr(cart, key):
                    setattr(cart, key, value)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Cart updated successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success' : False,
                'message' : 'Error updating cart',
                'data': {'error': str(e)}
            })
        
@cartBp.route('/cart/addtoorderproduct', methods=['POST'])
@jwt_required()
def addtoorderproduct():
    data = request.get_json()
    if data is None or 'product_ids' not in data:
        return jsonify({
            'success': False,
            'message': 'No product IDs provided'
        }), 400
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:    
                return jsonify({
                    'success': False,
                    'message': 'User not found'
            }), 404
            carts = session.query(Cart).filter(
                Cart.user_id == user.id,
                Cart.product_id.in_(data['product_ids'])
            ).all()
            if not carts:
                return jsonify({
                    'success': False,
                    'message': 'Selected products not found in cart'
                }), 404
            order_detail = OrderDetail(user_id=current_user['id'])
            session.add(order_detail)
            session.commit()
            for cart in carts:
                order_product = OrderProduct(
                    order_id=order_detail.id,
                    product_id=cart.product_id,
                    quantity=cart.quantity
                )
                session.add(order_product)
            session.commit()
            return jsonify({
                'success': True,
                'message': 'Selected products added to order product successfully'
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error adding selected products to order product',
                'data': {'error': str(e)}
            })
