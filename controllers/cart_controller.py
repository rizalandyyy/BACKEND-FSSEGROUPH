from flask import Blueprint, jsonify, request
from connectors.db import Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models.cart import Cart
from models.transaction_models.order_product import OrderProduct
from models.transaction_models.order_detail import OrderDetail
from models.user_models.user import User, Role_division
from models.product_models.product import Product


cartBp = Blueprint('cartBp',__name__)

@cartBp.route('/cart', methods=['GET'])
@jwt_required()
def cart():
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            if user.role not in [Role_division.customer]:
                return jsonify({
                    "success": False,
                    "message": "You are not a customer"
                }), 403

            cart_items = session.query(Cart).filter_by(user_id=user.id).all()
            if not cart_items:
                return jsonify({
                    'success': False,
                    'message': 'Cart is Empty'
                }), 404

            serialized_cart = []
            for item in cart_items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                if product:
                    serialized_cart.append({
                        'product_id': item.product_id,
                        'quantity': item.quantity,
                        'product_name': product.name,
                        'product_price': product.price,
                        'product_description': product.description,
                        'product_stock_qty': product.stock_qty,
                        'product_category_id': product.category_id,
                        'product_status': product.status.name,
                        'product_image': getattr(product, 'image', None)
                    })

            return jsonify({
                'success': True,
                'message': 'Cart retrieved successfully',
                'data': serialized_cart
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Error retrieving cart',
                'error': str(e)
            }), 500
                
    
    
@cartBp.route('/cart', methods=['POST'])
@jwt_required()
def addcart():
    data = request.get_json()
    if data is None:
        return jsonify({
            'success' : False,
            'message' : 'cart is empty'
        }), 400
        
    if 'product_id' not in data or 'quantity' not in data:
        return jsonify({
            'success': False,
            'message': 'Invalid request data'
        }), 400
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            print(user)
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            if user.role not in [Role_division.customer]:
                return jsonify({
                    "success": False,
                    "message": "You are not a customer"
                }), 403
                
            product = session.query(Product).filter_by(id=data['product_id']).first()
            print(product)
            if not product:
                return jsonify({
                    'success' : False,
                    'message': 'Product not found'
                }), 404
                
            if data['quantity'] > product.stock_qty:
                return jsonify({
                    "success": False,
                    "message": "Product quantity not enough"
                }), 400
                
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
            user = session.query(User).filter_by(userName= current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
            
            if user.role not in [Role_division.customer]:
                return jsonify({
                    "success": False,
                    "message": "You are not a customer"
                }), 403
            
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
            user = session.query(User).filter_by(userName = current_user['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'
                }), 404
                
            if user.role not in [Role_division.customer]:
                return jsonify({
                    "success": False,
                    "message": "You are not a customer"
                }), 403
                
            cart = session.query(Cart).filter_by(user_id=user.id, product_id=product_id).first()
            print(cart)
            if not cart:
                return jsonify({
                    'success' : False,
                    'message': 'Cart not found'
                }), 404
            
            cart.quantity = data['quantity']
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

#migrate to transaction controller
# @cartBp.route('/order', methods=['POST'])
# @jwt_required()
# def addtoorderproduct():
#     data = request.get_json()
#     if data is None or 'product_ids' not in data:
#         return jsonify({
#             'success': False,
#             'message': 'No product IDs provided'
#         }), 400
#     current_user = get_jwt_identity()
#     with Session() as session:
#         try:
#             user = session.query(User).filter_by(userName=current_user['userName']).first()
#             if not user:    
#                 return jsonify({
#                     'success': False,
#                     'message': 'User not found'
#             }), 404
            
#                 return jsonify({
#                     "success": False,
#                     "message": "You are not a customer"
#                 }), 403
                
#             carts = session.query(Cart).filter(
#                 Cart.user_id == user.id,
#                 Cart.product_id.in_(data['product_ids'])
#             ).all()
#             if not carts:
#                 return jsonify({
#                     'success': False,
#                     'message': 'Selected products not found in cart'
#                 }), 404
#             order_detail = OrderDetail(user_id=user.id, total_price=0, status=StatusEnum.pending, payment_id=1, user_id=user['id'])
#             session.add(order_detail)
#             for cart in carts:
#                 order_product = OrderProduct(
#                     order_id=order_detail.id,
#                     product_id=cart.product_id,
#                     quantity=cart.quantity
#                 )
#                 session.add(order_product)
#             session.commit()
#             return jsonify({
#                 'success': True,
                
#             }), 200
            
#         except Exception as e:
#             return jsonify({
#                 'success': False,
#                 'message': 'Error adding selected products to order product',
#                 'data': {'error': str(e)}
#             })

