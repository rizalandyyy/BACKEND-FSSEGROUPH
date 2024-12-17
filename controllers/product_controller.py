from flask import Blueprint, jsonify, request, current_app, send_file
from models.product_models.product import Product
from app import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.product_models.product_img import ProductImg
from models.product_models.product import Product
from models.user_models.user import User, Role_division
from models.product_models.list_category import ListCategory
from models.product_models.review import review
from decimal import Decimal
import os

productBp = Blueprint('productBp',__name__)


@productBp.route('/product', methods=['GET'])
def get_all_product():
    try:
        products = Product.query.all()
        
        serialized_product = [
            {
                "title": product.title,
                "ID" : product.id,
                "price": product.price,
                "stock_qty": product.stock_qty,
                "category": category.category if (category := ListCategory.query.get(product.category_id)) else None,
                "status": product.status.name,
                "description": product.description,
                "image": url.img_url if (url := ProductImg.query.filter_by(product_id=product.id).first()) else None,
                "seller": seller.userName if (seller := User.query.get(product.seller_id)) else None,
                "rating": (sum(r.rating for r in review.query.filter_by(product_id=product.id).all()) /
                           review.query.filter_by(product_id=product.id).count()) if review.query.filter_by(product_id=product.id).count() > 0 else None
                
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
@productBp.route('/product/seller/<user_id>', methods=['GET'])
def product_by_user(user_id):
    try:
        products = Product.query.filter_by(seller_id=user_id).all()        
        serialized_product = [
            {
                "title": product.title,
                "ID" : product.id,
                "price": product.price,
                "stock_qty": product.stock_qty,
                "category": category.category if (category := ListCategory.query.get(product.category_id)) else None,
                "status": product.status.name,
                "description": product.description,
                "image": url.img_url if (url := ProductImg.query.filter_by(product_id=product.id).first()) else None,
                "seller": seller.userName if (seller := User.query.get(product.seller_id)) else None,
                "rating": (sum(r.rating for r in review.query.filter_by(product_id=product.id).all()) /
                           review.query.filter_by(product_id=product.id).count()) if review.query.filter_by(product_id=product.id).count() > 0 else None
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
        }), 500
        
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
            "title": product.title,
                "ID" : product.id,
                "price": product.price,
                "stock_qty": product.stock_qty,
                "category": category.category if (category := ListCategory.query.get(product.category_id)) else None,
                "status": product.status.name,
                "description": product.description,
                "image": url.img_url if (url := ProductImg.query.filter_by(product_id=product.id).first()) else None,
                "seller": seller.userName if (seller := User.query.get(product.seller_id)) else None,
                "rating": (sum(r.rating for r in review.query.filter_by(product_id=product.id).all()) /
                           review.query.filter_by(product_id=product.id).count()) if review.query.filter_by(product_id=product.id).count() > 0 else None
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
    print(data)
    required_fields = ['title', 'price', 'stock_qty', 'category_id', 'description', 'status']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields: " + ", ".join(missing_fields)
        }), 400
    try:
        user = User.query.filter_by(id=current_user).first()
        if not user or user.role not in [Role_division.seller]:
            return jsonify({
                "success": False,
                "message": "You are not authorized to create a product"
            }), 403
        
        category = ListCategory.query.filter_by(id=data['category_id']).first()
        if not category:
            return jsonify({
                "success": False,
                "message": "Category not found"
            }), 404
        
                     
        new_product = Product(title=data['title'], price=Decimal(data['price']), stock_qty=str(data['stock_qty']), category_id=data['category_id'], description=data['description'], status=data['status'], seller_id=user.id)
        
        db.session.add(new_product)
        db.session.commit()    
        
        product_img = request.files['product_img']
        if not product_img or not product_img.filename:
            return jsonify({
                "success": False,
                "message": "No Product image file uploaded"
            }), 400
        
        filename = secure_filename(product_img.filename)
        file_path = os.path.join(current_app.root_path, 'images', str(new_product.id))
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_path = os.path.join(file_path, filename)
        product_img.save(file_path)

        img_url = f"{request.url_root}images/{new_product.id}/{filename}"
        add_img = ProductImg(product_id=new_product.id, file_path=file_path, file_name=filename, mime_type=product_img.mimetype, img_url=img_url)
        
        db.session.add(add_img)
        db.session.commit()
        
        product_data = {
            'id': new_product.id,
            'title': new_product.title,
            'price': str(new_product.price),
            'stock_qty': new_product.stock_qty,
            'category': category.category,
            'description': new_product.description,
            'status': new_product.status.name,
            'seller': user.userName,
            'image_url': img_url
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
        }), 500

@productBp.route('/images/<int:product_id>/<filename>')
def serve_image(product_id, filename):
    file_path = os.path.join(current_app.root_path, 'images', str(product_id), filename)
    return send_file(file_path, mimetype='image/jpeg')

# add new image to existing product (Not Used)
# @productBp.route('/product/<int:id>/addimage', methods=['POST'])
# @jwt_required()
# def addproductimage(id):
#     current_user = get_jwt_identity()
#     user = User.query.filter_by(id=current_user).first()
#     if not user:
#         return jsonify({
#             "success": False,
#             "message": "User not found"
#         }), 404
#     product = Product.query.filter_by(id=id, seller_id=user.id).first()
#     if not product:
#         return jsonify({
#             "success": False,
#             "message": "Product not found or you don't have permission to edit"
#         }), 404
#     add_img = request.files.get('product_img')
#     if not add_img:
#         return jsonify({
#             "success": False,
#             "message": "Error: No image file uploaded"
#         }), 400

#     filename = secure_filename(add_img.filename) if add_img.filename else ''
#     file_path = os.path.join(current_app.root_path, 'images', str(product.id))
#     if not os.path.exists(file_path):
#         os.makedirs(file_path)
#     file_path = os.path.join(file_path, filename)
    
#     add_img.save(file_path)
#     img_url = f"{request.url_root}images/{product.id}/{filename}"
    
#     new_img = ProductImg(product_id=product.id, file_path=file_path, file_name=filename, mime_type=add_img.mimetype, img_url=img_url)
#     db.session.add(new_img)
#     db.session.commit()

#     product_img_data = {
#         'id': new_img.id,
#         'product_id': new_img.product_id,
#         'name': new_img.file_name,
#         'img_url': new_img.img_url
#     }
    
#     return jsonify({
#         "success": True,
#         "message": "Product image added successfully",
#         "data": product_img_data
#     }), 201

@productBp.route('/product/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
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
        product = Product.query.filter_by(id=id, seller_id=current_user).first()
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
            'title': product.title,
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
    
