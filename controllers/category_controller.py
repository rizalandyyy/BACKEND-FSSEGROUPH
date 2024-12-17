from flask import Blueprint, jsonify, request, current_app, send_file
from models.product_models.product import Product
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.product_models.list_category import ListCategory

categoryBp = Blueprint('categoryBp',__name__)

@categoryBp.route('/category', methods=['GET'])
def get_category():
    try:
        categories = ListCategory.query.all()
        return jsonify({'categories': [category.to_dict() for category in categories]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        