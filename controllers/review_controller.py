from flask import Blueprint, jsonify, request, current_app, send_file
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product_models.review import review
from models.user_models.user import User, Role_division
from models.product_models.product import Product

reviewBp = Blueprint('reviewBp',__name__)

# add review to product
@reviewBp.route('/product/<int:product_id>/addreview', methods=['POST'])
@jwt_required()
def add_review(product_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    try:
        user = User.query.filter_by(id=current_user).first()
        if not user or user.role not in [Role_division.customer]:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404
        
        rating = data.get('rating', None)
        if rating is None or not 1 <= rating <= 5:
            return jsonify({
                "success": False,
                "message": "Invalid score. Please enter a score between 1 and 5."
            }), 400
        
        new_review = review()
        new_review.user_id = user.id
        new_review.product_id = product_id
        new_review.rating = rating
        db.session.add(new_review)
        db.session.commit()
        
        # calculate average review
        reviews = review.query.filter_by(product_id=product_id).all()
        total_score = sum(review.rating for review in reviews)
        average_score = total_score / len(reviews) if reviews else 0
        
        return jsonify({
            "success": True,
            "average_score": average_score
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
        
        
@reviewBp.route('/product/<int:product_id>/getreview', methods=['GET'])
def get_review(product_id):
    try:
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404
        
        reviews = product.reviews
        average_score = sum(review.score for review in reviews) / len(reviews) if reviews else 0
        
        return jsonify({
            "success": True,
            "rating": average_score
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500