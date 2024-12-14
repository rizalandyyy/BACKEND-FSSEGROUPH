from flask import Blueprint, jsonify, request
from models.product_models.product import Product
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.product_models.product_img import ProductImg
from models.product_models.product import Product
from models.user_models.user import User
from models.user_models.user import Role_division
from decimal import Decimal

productBp = Blueprint('productBp',__name__)


@productBp.route('/product', methods=['GET'])
def get_all_product():
    try:
        products = Product.query.all()
        serialized_product = [
            {
                "name": product.name,
                "price": product.price,
                "stock_qty": product.stock_qty,
                "category_id": product.category_id,
                "status": product.status.name,
                "description": product.description,
                "list_images": [
                              {
                                 "image": img.img 
                              }
                              for img in ProductImg.query.filter_by(product_id=product.id).all()
                            ]
            }
            for product in products
        ]
        return jsonify({
            "success": True,
            "message": "Products retrieved successfully",
            "data": serialized_product
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error retrieving products",
            "data": {"error": str(e)}
        })

@productBp.route('/product/<int:id>', methods=['GET'])
def product_by_id(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found",
                "data": {}
            }), 404
        serialized_product = {
            "name": product.name,
            "price": product.price,
            "stock_qty": product.stock_qty,
            "category_id": product.category_id,
            "status": product.status.name,
            "description": product.description
        }
        return jsonify({
            "success": True,
            "message": "Product retrieved successfully",
            "data": serialized_product
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error retrieving product",
            "data": {"error": str(e)}
        })
@productBp.route('/product/addproduct', methods=['POST'])
@jwt_required()
def create_product():
    current_user = get_jwt_identity()
  
    data = request.form
    required_fields = ['name', 'price', 'stock_qty', 'category_id', 'description', 'status']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields: " + ", ".join(missing_fields)
        }), 400
    try:
        user = User.query.filter_by(userName=current_user['userName']).first()
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        if user.role not in [Role_division.seller]:
            return jsonify({
                "success": False,
                "message": "You are not authorized to create a product"
            }), 403
        
        new_product = Product(name=data['name'], price=Decimal(data['price']), stock_qty=data['stock_qty'], category_id=data['category_id'], description=data['description'], status=data['status'], seller_id=user.id)
        db.session.add(new_product)
        db.session.commit()
        
        product_img = request.files['product_img']
        if product_img.filename is not None:
            filename = secure_filename(product_img.filename)
        mime_type = product_img.mimetype
        img_data = product_img.read()
        
        add_img = ProductImg(product_id=new_product.id, img=img_data, name=filename, mime_type=mime_type)
        db.session.add(add_img)
        db.session.commit()
        
        product_data = {
            'id': new_product.id,
            'name': new_product.name,
            'price': str(new_product.price),
            'stock_qty': new_product.stock_qty,
            'category_id': new_product.category_id,
            'description': new_product.description,
            'status': new_product.status.name,
            'seller_id': new_product.seller_id
        }
        return jsonify({
            "success": True,
            "message": "Product created successfully",
            "data": product_data
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error creating product",
            "data": {"error": str(e)}
        })
    
    
@productBp.route('/product/<int:id>/addimage', methods=['POST'])
@jwt_required()
def addproductimage(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(userName=current_user['userName']).first()
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404
    product = Product.query.filter_by(id=id, seller_id=user.id).first()
    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found or you don't have permission to edit"
        }), 404
    add_img = request.files['product_img']
    if not add_img:
        return jsonify({
            "success": False,
            "message": "Error: No image file uploaded"}), 400
    if add_img.filename is not None:
        filename = secure_filename(add_img.filename)
    mime_type = add_img.mimetype
    img_data = add_img.read()
    
    # Decode the image data
    img_data = img_data.decode('utf-8')
    
    add_img = ProductImg(product_id=product.id, img=img_data, name=filename, mime_type=mime_type)
    db.session.add(add_img)
    db.session.commit()
    
    product_img_data = {
        'id': add_img.id,
        'product_id': add_img.product_id,
        'name': add_img.name,
        'mime_type': add_img.mime_type
    }
    
    return jsonify({
        "success": True,
        "message": "Product image added successfully",
        "data": product_img_data
    }), 201

@productBp.route('/product/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(userName=current_user['userName']).first()
    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }),404
    product_img = ProductImg.query.filter_by(product_id=id).all()
    if not product_img:
        return jsonify({
            "success": False,
            "message": "image not found or you don't have permission to delete"
        }), 403
    for img in product_img:
        db.session.delete(img)
    db.session.commit()
        
    product = Product.query.filter_by(id=id, seller_id=user.id).first()
    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found or you don't have permission to delete"
        }), 403
    db.session.delete(product)
    db.session.commit()
        
    return jsonify({
        "success": True,
        "message": "Product deleted successfully"
    }), 200

            
@productBp.route('/product/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    current_user = get_jwt_identity()
    
    try:
        product = Product.query.filter_by(id=id, seller_id=current_user['id']).first()
        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found or you don't have permission to edit"
            }), 403
        data = request.form
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        db.session.commit()
        Serialized_product = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock_qty': product.stock_qty,
            'category_id': product.category_id
        }
        
        return jsonify({
            "success": True,
            "message": "Product updated successfully",
            "data": Serialized_product
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error updating product",
            "data": {"error": str(e)}
        }), 500



