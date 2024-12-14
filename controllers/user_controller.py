from flask import Blueprint, request, jsonify, current_app
from app import db
import datetime
from models.user_models.user import User
from models.user_models.secret_question import SecretQuestion
from models.user_models.master_question import MasterQuestion
from models.user_models.avatar_img import AvatarImg
from models.user_models.address_location import AddressLocation
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bcrypt import gensalt, hashpw
import os


userBp = Blueprint('userBp',__name__)

# register user
@userBp.route('/register', methods=['POST'])
def register():
    data = request.form
    print(data)
    required_fields = ['firstName', 'lastName', 'userName', 'email', 'gender', 'phoneNumber', 'password', 'role', 'address', 'question', 'answer']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields: " + ", ".join(missing_fields)
        }), 400

    try:
        user = User.query.filter_by(userName=data['userName']).first()
        if user:
            return jsonify({
                "success": False,
                "message": "Username already exists"}), 400

        email = User.query.filter_by(email=data['email']).first()
        if email:
            return jsonify({
                "success": False,
                "message": "Email already exists"}), 400

        new_user = User(
            firstName=data['firstName'],
            lastName=data['lastName'],
            userName=data['userName'],
            email=data['email'],
            role=data['role'],
            gender=data['gender'],
            phoneNumber=data['phoneNumber']
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.flush()  # To generate the new user's ID

        add_address = AddressLocation(user_id=new_user.id, address=data['address'])
        db.session.add(add_address)

        master_question = MasterQuestion.query.filter_by(id=data['question']).first()
        if not master_question:
            return jsonify({
                "success": False,
                "message": "Question not found"}), 404

        secret_question = SecretQuestion(user_id=new_user.id, question_id=master_question.id, answer=data['answer'])
        db.session.add(secret_question)

        avatar_image = 'blank-male-avatar.png' if data['gender'] == 'Male' else 'blank-female-avatar.png'
        avatar_path = os.path.join(current_app.root_path, 'asset', avatar_image)

        if not os.path.isfile(avatar_path):
            return jsonify({
                "success": False,
                "message": "Avatar image not found"}), 400

        with open(avatar_path, 'rb') as f:
            avatar_img_data = f.read()

        avatar_img = AvatarImg(user_id=new_user.id, img=avatar_img_data)
        db.session.add(avatar_img)

        db.session.commit()
        return jsonify({
            "success": True,
            "message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error registering user",
            "data": {"error": str(e)}
        }), 500

@userBp.route('/userprofile' , methods=['GET'])
def userprofile():
    try:
        users = User.query.all()
        serialized_users = [
            {
                'id': user.id,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'userName': user.userName,
                'email': user.email,
                'phoneNumber': user.phoneNumber,
                'gender': user.gender.value,
                'role': user.role.value,
                'addresses': [
                    {
                        'address': address.address
                    }
                    for address in user.addresses
                ]
            }
            for user in users
        ]
        return jsonify({
            "success": True,
            "message": "User retrieved successfully",
            "data": serialized_users
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error retrieving user",
            "data": {"error": str(e)}
        }), 500

# login user
@userBp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None:
        return jsonify({
            "success": False,
            "message": "No data received"}),400
    
    if 'userName' not in data or 'password' not in data:
        return jsonify({
            "success": False,
            "message": "Missing required fields"}),400
    
    try:
        user = User.query.filter_by(userName=data['userName']).first()
        if user and user.check_password(data['password']):
            expires = datetime.timedelta(minutes=60)
            access_token = create_access_token(identity={
                'id': user.id,
                'userName': user.userName,
            }, expires_delta=expires)
            return jsonify({
                'success' : True,
                'message': f'User {user.userName} logged in successfully',
                'access_token': access_token,
                'role': user.role.name,
                'user_id': user.id
            }), 201

        return jsonify({'error': 'Invalid username or password'}), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error logging in user",
            "data": {"error": str(e)}
        }), 404
        
@userBp.route('/userprofile/<user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success' : False,
                'message': 'User not found'}), 404
        return jsonify({
            'success' : True,
            'message': 'User retrieved successfully',
            'data': {
                'id': user.id,
                'firstName': user.firstName,
                'lastName': user.lastName,
                'userName': user.userName,
                'email': user.email,
                'phoneNumber': user.phoneNumber,
                'gender': user.gender.value,
                'role': user.role.value,
                'addresses': [
                    {
                        'address': address.address
                    }
                    for address in user.addresses
                ]
            }
        }), 200
    except Exception as e:
        return jsonify({
        "success": False,
        "message": "Error retrieving user",
        "data": {"error": str(e)}}), 404
            

#if user forgot password
@userBp.route('/login/forgotpassword', methods=['POST'])
def forgotpassword():
    data = request.get_json()
    if data is None:
        return jsonify({
            'success' : False,
            'message': 'Error, Please fill in the form to search for your account'}),400
    
    if 'userName' not in data:
        return jsonify({
            'success' : False,
            'message': 'Error, wrong input'}), 400
    
    if 'password' not in data:
        return jsonify({
            'success' : False,
            'message' : 'Error, fill the password'}), 400
    
    if 'repeat_password' not in data:
        return jsonify({
            'success' : False,
            'message' : 'Error,fill the repeat password'}), 400
    
    if data['password'] != data['repeat_password'] :
        return jsonify({
            'success' : False,
            'message': 'password and repeat password not same'}), 400
    print(data)
    try:            
        user = User.query.filter_by(userName=data['userName']).first()
        if user is None:
            return jsonify({
                'success' : False,
                'message': 'User not found'}), 404
         
        secret_question = user.secret_questions.filter_by(question_id=data['question']).first()
        if not secret_question:
            return jsonify({
                'success' : False,
                'message': 'Wrong Secret Question'}), 404
         
        master_question = MasterQuestion.query.get(secret_question.question_id)
        if not master_question:
            return jsonify({
                'success' : False,
                'message': 'Master question not found'}), 404
            
        if master_question.id == data['question'] and secret_question.answer == data['answer']:
            user.password = hashpw(data['password'].encode('utf-8'), gensalt()).decode('utf-8')
            db.session.commit()
            return jsonify({
                'success' : True,
                'message': 'Password Updated'}), 200
            
        else:
            return jsonify({
                'success' : False,
                'message': 'Answer is incorrect'}), 400
            
            
    except Exception as e:
        return jsonify({
        "success": False,
        "message": "user not found",
        "data": {"error": str(e)}}), 404

# logout user
@userBp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({
        'success' : True,
        'message': 'User logged out successfully'}), 200
         
         
# update password of user
@userBp.route('/updatepassword', methods=['PUT'])
@jwt_required()
def updatepassword():
    data = request.get_json()
    if data is None:
        return jsonify({
            'success': False,
            'Message': 'Please fill in the form to search for your account'
        }), 400
    
    if 'password' not in data:
        return jsonify({
            'success': False,
            'message': 'Error, wrong input'
        }), 400
    
    try:
        user = User.query.filter_by(userName=data['userName']).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user.set_password(data['password'])
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Password updated successfully'
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error updating password",
            "data": {"error": str(e)}
        }), 404
# add new address
@userBp.route('/addaddress', methods=['POST'])
@jwt_required()
def addaddress():
    data = request.get_json()
    current_user = get_jwt_identity()
    
    if 'address' not in data:
        return jsonify({
            'success' : False,
            'message': 'Error, wrong input'}), 400
    
    try:            
        user = User.query.filter_by(userName=current_user['userName']).first()
        if not user:
            return jsonify({
                'success' : False,
                'message': 'User not found'}), 404
                
        add_address = AddressLocation(user_id=user.id, address=data['address'])
        db.session.add(add_address)
        db.session.commit()
        return jsonify({
            'success' : True,
            'message': 'Address added successfully'}), 200
    except Exception as e:
        return jsonify({
        "success": False,
        "message": "Error adding address",
        "data": {"error": str(e)}}), 404

            
# delete address
@userBp.route('/deleteaddress/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteaddress(id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(userName=current_user['userName']).first()
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404

    address = AddressLocation.query.filter_by(user_id=user.id, id=id).first()
    if not address:
        return jsonify({
            'success': False,
            'message': 'Address not found'
        }), 404

    db.session.delete(address)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Address deleted successfully'
    }), 200

            
#update user profile
@userBp.route('/userprofile', methods=['PUT'])
@jwt_required()
def updateuserprofile():
    current_user = get_jwt_identity()
    try:
        user = User.query.filter_by(userName=current_user['userName']).first()
        if not user:
            return jsonify({
                'success' : False,
                'message': 'User not found'}), 404

        for key, value in request.form.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()

        serialized_user = {
            'id': user.id,
            'firstName': user.firstName,
            'lastName': user.lastName,
            'userName': user.userName,
            'email': user.email,
            'phoneNumber': user.phoneNumber
        }      
        return jsonify({
            "success": True,
            "message": "User update successfully",
            "data": serialized_user
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error updating user profile",
            "error":  str(e)}), 500


