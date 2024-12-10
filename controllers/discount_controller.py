from flask import Blueprint, jsonify, request
from models.user_models.user import User, Role_division
from connectors.db import Session
from models.transaction_models.discount import DiscountCode
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import pytz

discountBp = Blueprint('discountBp',__name__)


@discountBp.route('/discounts', methods=['GET'])
def discounts():
    with Session() as session:
        try:
            discount = session.query(DiscountCode).all()
            discount_list = [{
                'id':dl.id ,
                'code':dl.code ,
                'discount_value':dl.discount_value,
                'expiration_date' : dl.expiration_date,
                'seller_id' : dl.seller_id,
                'status' : dl.status
                }
                for dl in discount
            ] 
            return jsonify ({
                "success" : True,
                "message" : "Discount list retrieve successfully",
                "data" : discount_list
            })
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error retrieving Discount list",
            "data": {"error": str(e)}
        }), 500

@discountBp.route('/discount/getdiscount', methods=['POST'])
def discount():
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "message": "Missing required fields: seller_id",
        }), 400
    with Session() as session:
        try:
            discount = session.query(DiscountCode).filter_by(seller_id=data['seller_id']).all()
            discount_list = [{
                'id':dl.id ,
                'code':dl.code ,
                'discount_value':dl.discount_value,
                'expiration_date' : dl.expiration_date,
                'seller_id' : dl.seller_id,
                'status' : dl.status
                }
                for dl in discount
            ] 
            return jsonify ({
                "success" : True,
                "message" : "Discount list retrieve successfully",
                "data" : discount_list
            })
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error retrieving Discount list",
            "data": {"error": str(e)}
        }), 500

@discountBp.route('/discount' , methods = ['POST'])
@jwt_required()
def adddiscount():
    current_user = get_jwt_identity()
    data = request.get_json()
    required_fields = ['code', 'discount_value', 'expiration_date']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields: " + ", ".join(missing_fields)
        }), 400
    
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404
                
            if user.role not in [Role_division.seller]:
                return jsonify({
                    "success": False,
                    "message": "You are not authorized to create a discount"
                }), 403
            
            expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d')
            expiration_date = pytz.utc.localize(expiration_date)
            today = datetime.now(pytz.utc)
            if expiration_date < today:
                return jsonify({
                    "success": False,
                    "message": "Expiration date must be in the future"
                }), 400
                           
                   
            new_discount = DiscountCode(code = data['code'], discount_value = data['discount_value'], expiration_date= expiration_date, status='pending', seller_id = user.id)
            
            if expiration_date > today:
                new_discount.status = 'available'
            else:
                new_discount.status = 'expired'
            
            
            session.add(new_discount)   
            session.commit()
            
            discount_data = {
                'id' : new_discount.id,
                'code' : new_discount.code,
                'discount_value' : new_discount.discount_value,
                'expiration_date' : new_discount.expiration_date,
                'status' : new_discount.status,
                'seller_id' : new_discount.seller_id
            }
            
            return jsonify({
                "success" : True,
                "message" : "Discount created successfully",
                "data" : discount_data
            }), 201
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error creating product",
                "data": {"error": str(e)}
            }), 500

@discountBp.route('/discount/<int:id>', methods=['DELETE'])
@jwt_required()
def deletediscount(id):
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404
                
            if user.role not in [Role_division.seller]:
                return jsonify({
                    "success": False,
                    "message": "You are not authorized to delete a discount"
                }), 403
                
            discount = session.query(DiscountCode).filter_by(id=id, seller_id=user.id).first()
            if not discount:
                return jsonify({
                    "success": False,
                    "message": "Discount not found"
                }), 404
                
            session.delete(discount)
            session.commit()
            return jsonify({
                "success": True,
                "message": "Discount deleted successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error deleting discount",
                "data": {"error": str(e)}
            }), 500
            
@discountBp.route('/discount/<int:id>', methods=['PUT'])
@jwt_required()
def updatediscount(id):
    current_user = get_jwt_identity()
    data = request.get_json()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404
                
            if user.role not in [Role_division.seller]:
                return jsonify({
                    "success": False,
                    "message": "You are not authorized to update a discount"
                }), 403
                
            discount = session.query(DiscountCode).filter_by(id=id, seller_id=user.id).first()
            if not discount:
                return jsonify({
                    "success": False,
                    "message": "Discount not found"
                }), 404
                
            for key, value in data.items():
                if hasattr(discount, key):
                    setattr(discount, key, value)
            
            discount.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d').replace(tzinfo=pytz.utc)    
            today = datetime.now(pytz.utc)
            if discount.expiration_date > today:
                discount.status = 'available'
            else:
                discount.status = 'expired'
            session.commit()
            serialized_discount = {
                'id': discount.id,
                'code': discount.code,
                'discount_value': discount.discount_value,
                'expiration_date': discount.expiration_date,
                'status': discount.status,
                'seller_id': discount.seller_id
            }
            return jsonify({
                "success": True,
                "message": "Discount updated successfully",
                "data": serialized_discount
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error updating discount",
                "data": {"error": str(e)}
            }), 500


           
@discountBp.route('/refreshdiscount', methods=['POST'])
@jwt_required()
def refreshdiscount():
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user['userName']).first()
            if not user:
                return jsonify({
                    "success": False,
                    "message": "User not found"
                }), 404
                
            if user.role not in [Role_division.seller]:
                return jsonify({
                    "success": False,
                    "message": "You are not authorized to refresh a discount"
                }), 403
                
            discount = session.query(DiscountCode).filter_by(seller_id=user.id).all()
            if not discount:
                return jsonify({
                    "success": False,
                    "message": "Discount not found"
                }), 404
                
            today = datetime.now(timezone.utc)
            for d in discount:
                if session.query(DiscountCode).filter(DiscountCode.id == d.id, d.expiration_date < today).first():
                    d.status = 'expired'
                else:
                    d.status = 'available'
            session.commit()
            return jsonify({
                "success": True,
                "message": "Discount status refreshed successfully",
                "data": discount
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error refreshing discount status",
                "data": {"error": str(e)}
            }), 500
            