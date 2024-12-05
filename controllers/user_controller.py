from flask import Blueprint, request, jsonify
from sqlalchemy import text
import datetime
from models.user_models.user import User
from models.user_models.secret_question import SecretQuestion
from models.user_models.master_question import MasterQuestion
from models.user_models.avatar_img import AvatarImg
from models.user_models.address_location import AddressLocation
from connectors.db import Session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from bcrypt import gensalt, hashpw
from werkzeug.utils import secure_filename


userBp = Blueprint('userBp',__name__)

# register user
@userBp.route('/register', methods=['POST'])
def register():
    data = request.form
    # return jsonify ({"data": data})
    if not data or 'firstName' not in data or 'lastName' not in data or 'userName' not in data or 'email' not in data or 'gender' not in data or 'phoneNumber' not in data or 'password' not in data or 'role' not in data or 'address' not in data or 'question' not in data or 'answer' not in data:
        return jsonify({
            "success": False,
            "message": "there are missing parameters"}), 400
    
    try:    
        with Session() as session:
            user = session.query(User).filter_by(userName=data['userName']).first()
            if user:
                return jsonify({
            "success": False,
            "message": "Username already exists"}), 400
            
            email = session.query(User).filter_by(email=data['email']).first()
            if email:
                return jsonify({
            "success": False,
            "message": "Email already exists"}), 400
            
            New_user = User(firstName = data['firstName'], lastName=data['lastName'], userName=data['userName'], email=data['email'], role=data['role'], gender=data['gender'], phoneNumber=data['phoneNumber'])
            New_user.set_password(data['password'])
            
            session.add(New_user)
            session.commit()
            
            add_address = AddressLocation(user_id=New_user.id, address=data['address'])
            session.add(add_address)
            session.commit()
            
            secret_question = SecretQuestion(user_id=New_user.id, question_id=data['question'], answer=data['answer'])
            session.add(secret_question)
            session.commit()
            
                                   
            return jsonify({
            "success": True,
            "message": "User registered successfully"}), 201
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error registering user",
            "data": {"error": str(e)}
        }), 500

@userBp.route('/userprofile' , methods=['GET'])
def userprofile():
    try:
        with Session() as session:
            users = session.query(User).all()
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
                        for address in session.query(AddressLocation).filter_by(user_id=user.id).all()
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
    
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=data['userName']).first()
            session.execute(text('SELECT * FROM user where userName = userName and password = password'), {
                'userName': data['userName'],
                'password': data['password']
            })
            if user and user.check_password(data['password']):
                expires = datetime.timedelta(minutes=60)
                access_token = create_access_token(identity={
                    'id': user.id,
                    'userName': user.userName,
                }, expires_delta=expires)
                return jsonify({
                    'success' : True,
                    'message': f'User {user.userName} logged in successfully',
                    'access_token': access_token
                }), 201

            return jsonify({'error': 'Invalid email or password'}), 400
        except Exception as e:
            
            return jsonify({
            "success": False,
            "message": "Error logging in user",
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
    
    with Session() as session:
        try:            
            user = session.query(User).filter_by(userName=data['userName']).first()
            
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'}), 404

            secret_question = session.query(SecretQuestion).filter_by(user_id=user.id).first()
            if not secret_question:
                return jsonify({
                    'success' : False,
                    'message': 'Wrong Secret Question'}), 404

            master_question = session.query(MasterQuestion).filter_by(id=secret_question.question_id).first()
            if not master_question:
                return jsonify({
                    'success' : False,
                    'message': 'Master question not found'}), 404

            if master_question.question == data['question'] and secret_question.answer == data['answer']:
                hashed_password = hashpw(data['password'].encode('utf-8'), gensalt()).decode('utf-8')
                user.password = hashed_password
                session.commit()
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
            'success' : False,
            'Message': 'Please fill in the form to search for your account'}),400
    
    if 'password' not in data:
        return jsonify({
            'success' : False,
            'message': 'Error, wrong input'})
    
    with Session() as session:
        try:            
            user = session.query(User).filter_by(userName=data['userName']).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'}), 404
                
            user.set_password(data['password'])
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Password updated successfully'}), 200
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error updating password",
            "data": {"error": str(e)}}), 404     
                   
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
    
    with Session() as session:
        try:            
            user = session.query(User).filter_by(userName=current_user).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'}), 404
                
            add_address = AddressLocation(user_id=user.id, address=data['address'])
            session.add(add_address)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Address added successfully'}), 200
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error adding address",
            "data": {"error": str(e)}}), 404
            
# delete address
@userBp.route('/deleteaddress', methods=['DELETE'])
@jwt_required()
def deleteaddress():
    data = request.get_json()
    current_user = get_jwt_identity()
    if 'address' not in data:
        return jsonify({
            'success' : False,
            'message': 'Error, wrong input'}), 400
    
    with Session() as session:
        try:            
            user = session.query(User).filter_by(userName=current_user).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'}), 404
                
            address = session.query(AddressLocation).filter_by(address=data['address']).first()
            if not address:
                return jsonify({
                    'success' : False,
                    'message': 'Address not found'}), 404
                
            session.delete(address)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'Address deleted successfully'}), 200
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error deleting address",
            "data": {"error": str(e)}}), 404
            
#update user profile
@userBp.route('/userprofile', methods=['PUT'])
@jwt_required()
def updateuserprofile():
    data = request.get_json()
    current_user = get_jwt_identity()
    with Session() as session:
        try:
            user = session.query(User).filter_by(userName=current_user).first()
            if not user:
                return jsonify({
                    'success' : False,
                    'message': 'User not found'}), 404
            
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            return jsonify({
                'success' : True,
                'message': 'User profile updated successfully'}), 200
        except Exception as e:
            return jsonify({
            "success": False,
            "message": "Error updating user profile",
            "data": {"error": str(e)}}), 404
