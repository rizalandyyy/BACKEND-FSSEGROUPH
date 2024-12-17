from flask import Blueprint, jsonify, request
from models.user_models.user import User, Role_division
from app import db
from models.transaction_models.discount_code import DiscountCode
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import pytz

discountBp = Blueprint('discountBp',__name__)


@discountBp.route('/discounts', methods=['GET'])
def discounts():
    try:
        discounts = DiscountCode.query.all()
        discount_list = [{
            'id':dl.id ,
            'code':dl.code ,
            'discount_value':dl.discount_value,
            'expiration_date' : dl.expiration_date,
            'seller_id' : dl.seller_id,
            'status' : dl.status
            }
            for dl in discounts
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
    try:
            discount = DiscountCode.query.filter_by(seller_id=data['seller_id']).all()
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

@discountBp.route('/discount', methods=['POST'])
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
    
    user = User.query.filter_by(id=current_user).first()
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
                           
    status = 'available' if expiration_date > today else 'expired'
    new_discount = DiscountCode(code=data['code'], discount_value=data['discount_value'], expiration_date=expiration_date, status=status, seller_id=user.id)
            
    db.session.add(new_discount)   
    db.session.commit()
            
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
    

@discountBp.route('/discount/<int:id>', methods=['DELETE'])
@jwt_required()
def deletediscount(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
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
          
    discount = DiscountCode.query.filter_by(id=id, seller_id=user.id).first()
    if not discount:
        return jsonify({
            "success": False,
            "message": "Discount not found"
        }), 404
          
    db.session.delete(discount)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Discount deleted successfully"
    }), 200

            
@discountBp.route('/discount/<int:id>', methods=['PUT'])
@jwt_required()
def updatediscount(id):
    current_user = get_jwt_identity()
    data = request.get_json()
    required_fields = ['code', 'discount_value', 'expiration_date']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields: " + ", ".join(missing_fields)
        }), 400
    
    try:
        user = User.query.filter_by(id=current_user).first()
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
            
        discount = DiscountCode.query.filter_by(id=id, seller_id=user.id).first()
        if not discount:
            return jsonify({
                "success": False,
                "message": "Discount not found"
            }), 404
            
        expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d').replace(tzinfo=pytz.utc)
        today = datetime.now(pytz.utc)
        status = 'available' if expiration_date > today else 'expired'
        
        discount.code = data['code']
        discount.discount_value = data['discount_value']
        discount.expiration_date = expiration_date
        discount.status = status
        
        db.session.commit()
        
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
    try:
        user = User.query.filter_by(id=current_user).first()
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
                
        discount = DiscountCode.query.filter_by(seller_id=user.id).all()
        if not discount:
            return jsonify({
                "success": False,
                "message": "Discount not found"
            }), 404
                
        today = datetime.now(timezone.utc)
        for d in discount:
            d.status = 'expired' if d.expiration_date < today else 'available'
        db.session.commit()
        
        serialized_discount = [
            {
                'id': d.id,
                'code': d.code,
                'discount_value': d.discount_value,
                'expiration_date': d.expiration_date,
                'status': d.status,
                'seller_id': d.seller_id
            }
            for d in discount
        ]
        
        return jsonify({
            "success": True,
            "message": "Discount status refreshed successfully",
            "data": serialized_discount
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error refreshing discount status",
            "data": {"error": str(e)}
        }), 500

            