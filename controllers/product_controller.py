from flask import Blueprint, jsonify, request
from models.product_models.product import Product
from connectors.db import Session
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models.product_models.product_img import ProductImg

productBp = Blueprint('productBp',__name__)


@productBp.route('/product', methods=['GET'])
def product():
    try:
        with Session() as session:
            products = session.query(Product).all()
            return jsonify({
                "success": True,
                "message": "Products retrieved successfully",
                "data": products
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
        with Session() as session:
            product = session.query(Product).filter_by(id=id).first()
            return jsonify({
                "success": True,
                "message": "Product retrieved successfully",
                "data": product
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
    if current_user['role'] != 'seller':
        return jsonify({
            "success": False,
            "message": "Only seller can post product"
        }), 403
    data = request.form
    if data is None or 'name' not in data or 'description' not in data or 'price' not in data or 'quantity' not in data or 'category_id' not in data:
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400
    
    try:
        with Session() as session:
            product = Product(name=data['name'], description=data['description'], price=data['price'], stock_qty=data['quantity'], category_id=data['category_id'])
            session.add(product)
            session.commit()
            
            product_img = request.files['product_img']
            if not product_img:
                return jsonify({
                    "success": False,
                    "message": "Error: No image file uploaded"}), 400
                
            if product_img.filename is not None:
                filename = secure_filename(product_img.filename)
                product_img.save('static/images/product/' + filename)
            mime_type = product_img.mimetype
            img_data = product_img.read()
            
            add_img = ProductImg(product_id=product.id, img=img_data, name=filename, mime_type=mime_type)
            session.add(add_img)
            session.commit()
            
            return jsonify({
                "success": True,
                "message": "Product created successfully",
                "data": product
            }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error creating product",
            "data": {"error": str(e)}
        })

@productBp.route('/product/addimageproduct<int:id>', methods=['POST'])
@jwt_required()
def addproductimage(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'seller':
        return jsonify({
            "success": False,
            "message": "Only seller can edit product"
        }), 403
        
    add_img = request.files['product_img']
    if not add_img:
        return jsonify({
            "success": False,
            "message": "Error: No image file uploaded"}), 400
    with Session() as session:
        try:
            product = session.query(Product).filter_by(id=id).first()
            if not product:
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404
            
            if add_img.filename is not None:
                filename = secure_filename(add_img.filename)
                add_img.save('static/images/product/' + filename)
            mime_type = add_img.mimetype
            img_data = add_img.read()
            
            add_img = ProductImg(product_id=product.id, img=img_data, name=filename, mime_type=mime_type)
            session.add(add_img)
            session.commit()
            
            return jsonify({
                "success": True,
                "message": "Product image added successfully",
                "data": add_img
            }), 201
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error adding product image",
                "data": {"error": str(e)}
            })

@productBp.route('/product/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'seller':
        return jsonify({
            "success": False,
            "message": "Only seller can delete product"
        }), 403
    with Session() as session:
        try:
            product = session.query(Product).filter_by(id=id).first()
            if not product:
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404
            
            session.delete(product)
            session.commit()
            
            return jsonify({
                "success": True,
                "message": "Product deleted successfully"
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error deleting product",
                "data": {"error": str(e)}
            })
            
@productBp.route('/product/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'seller':
        return jsonify({
            "success": False,
            "message": "Only seller can edit product"
        }), 403
    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    with Session() as session:
        try:
            product = session.query(Product).filter_by(id=id).first()
            if not product:
                return jsonify({
                    "success": False,
                    "message": "Product not found"
                }), 404

            for key, value in data.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            session.commit()

            return jsonify({
                "success": True,
                "message": "Product updated successfully",
                "data": product
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "message": "Error updating product",
                "data": {"error": str(e)}
            })
