from flask import Blueprint, jsonify, request
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user_models.user import User, Role_division
from models.transaction_models.payment_method import PaymentMethod
from models.transaction_models.transaction_detail_customer import TrasactionDetailCustomer
from models.transaction_models.discount_code import DiscountCode
from models.transaction_models.order_product import OrderProduct
from models.product_models.product import Product

transactionBp = Blueprint('transactionBp',__name__)

# create transaction
@transactionBp.route('/transaction', methods=['POST'])
@jwt_required()
def create_order_transaction():
    current_user = get_jwt_identity()
    data = request.get_json()

    #cek if data is None
    if not data:
        return jsonify({"success": False, "message": "Missing JSON payload"}), 400

    #cek if required fields are present
    required_fields = ['payment_method_id', 'discount_code', 'products']
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

    try:
        #cek if user exist and have role customer
        user = User.query.filter_by(id=current_user).first()
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        if user.role not in [Role_division.customer]:
            return jsonify({
                "success": False,
                "message": "You are not authorized to create an order product"
            }), 403

        #cek if payment method exist
        payment_method = PaymentMethod.query.filter_by(id=data['payment_method_id']).first()
        if not payment_method:
            return jsonify({
                "success": False,
                "message": "Payment method not found"
            }), 404

        #cek if discount code exist
        discount = DiscountCode.query.filter_by(code=data['discount_code']).first()
        if not discount:
            return jsonify({
                "success": False,
                "message": "Discount code not found"
            }), 404
        
        # create order transaction
        order_products = []
        total_price = 0
        for product_data in data['products']:
            if 'product_id' not in product_data or 'quantity' not in product_data:
                return jsonify({
                    "success": False,
                    "message": "Missing required fields: product_id and quantity"
                }), 400

            product = Product.query.filter_by(id=product_data['product_id']).first()
            if not product:
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404

            sum_price = product.price * product_data['quantity']
            total_price += sum_price

            order_product = OrderProduct(
                customer_id=user.id,
                product_id=product.id,
                quantity=product_data['quantity'],
                sum_price=sum_price,
                seller_id=product.seller_id
            )

            order_products.append(order_product)
            db.session.add(order_product)
            db.session.commit()

        #Apply discount
        discount_value = discount.discount_value
        total_price -= discount_value
        
        transaction_detail = TrasactionDetailCustomer(
            user_id=user.id,
            payment_id=payment_method.payment_method,
            total_price=total_price,
            status="pending"
        )
        db.session.add(transaction_detail)
        db.session.commit()

        for order_product in order_products:
            order_product.order_id = transaction_detail.id
            db.session.add(order_product)
            db.session.commit()

        serialized_order_products = []
        for order_product in order_products:
            seller = User.query.filter_by(id=order_product.seller_id).first()
            if not seller:
                return jsonify({
                    "success": False,
                    "message": "Seller not found"
                }), 404

            serialized_order_product = {
                "id": order_product.id,
                "order_id": order_product.order_id,
                "customer": user.userName,
                "product_id": order_product.product_id,
                "quantity": order_product.quantity,
                "sum_price": order_product.sum_price,
                "seller": seller.userName
            }
            serialized_order_products.append(serialized_order_product)

        serialized_transaction_detail = {
            "id": transaction_detail.id,
            "user_id": transaction_detail.user_id,
            "payment_id": transaction_detail.payment_id,
            "total_price": transaction_detail.total_price,
            "status": transaction_detail.status
        }

        return jsonify(
            {
                "success": True,
                "message": "Transaction and order created successfully",
                "data_product": serialized_order_products,
                "data_transaction": serialized_transaction_detail
            }
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
    finally:
        db.session.close()
        
@transactionBp.route('/transaction', methods=['GET'])
@jwt_required()
def get_transaction():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    if user.role not in [Role_division.customer]:
        return jsonify({
            "success": False,
            "message": "You are not authorized to get transaction"
        }), 403
    transactions = TrasactionDetailCustomer.query.filter_by(user_id=user.id).all()
    serialized_transactions = []
    for transaction in transactions:
        order_products = OrderProduct.query.filter_by(order_id=transaction.id).all()
        serialized_order_products = []
        for order_product in order_products:
            seller = User.query.filter_by(id=order_product.seller_id).first()
            if not seller:
                return jsonify({
                    "success": False,
                    "message": "Seller not found"
                }), 404
            product = Product.query.filter_by(id=order_product.product_id).first()
            if not product:
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404
            serialized_order_product = {
                "product_name": product.title,
                "quantity": order_product.quantity,
                "sum_price": order_product.sum_price,
                "seller": seller.userName
            }
            serialized_order_products.append(serialized_order_product)
        payment_method = PaymentMethod.query.filter_by(payment_method=transaction.payment_id).first()
        if not payment_method:  
            return jsonify({
                "success": False,
                "message": "Payment method not found"
            }), 404
        
        serialized_transaction = {
            "id": transaction.id,
            "customer": user.userName,
            "payment_method": payment_method.payment_method,
            "total_price": transaction.total_price,
            "status": transaction.status,
            "order_products": serialized_order_products
        }
        serialized_transactions.append(serialized_transaction)
    return jsonify({
        "success": True,
        "message": "Transaction retrieved successfully",
        "data": serialized_transactions
    })
    
# @transactionBp.route('/transaction/<int:transaction_id>', methods=['POST'])
# @jwt_required()
# def update_transaction(transaction_id):
#     current_user = get_jwt_identity()
#     user = User.query.filter_by(id=current_user).first()
#     if not user:
#         return jsonify({
#             "success": False,
#             "message": "User not found"
#         }), 404
#     if user.role not in [Role_division.seller]:
#         return jsonify({
#             "success": False,
#             "message": "You are not authorized to update transaction"
#         }), 403