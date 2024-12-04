from flask import Blueprint, request, jsonify
from sqlalchemy import text
import datetime
from models.user_models.user import User
from models.user_models.secret_question import SecretQuestion
from models.user_models.master_question import MasterQuestion
from models.user_models.avatar_img import AvatarImg
from models.user_models.address_location import AddressLocation
from connectors.db import Session
from flask_jwt_extended import create_access_token, jwt_required
from bcrypt import gensalt, hashpw
from werkzeug.utils import secure_filename


userBp = Blueprint('userBp',__name__)

# register user
@userBp.route('/register', methods=['POST'])
def register():
    data = request.form
    # return jsonify ({"data": data})
    if not data or 'username' not in data or 'email' not in data or 'password' not in data or 'role' not in data or 'address' not in data or 'question' not in data or 'answer' not in data:
        return jsonify({
            "success": False,
            "message": "Missing username, email, password, role, or address"}), 400
    
    try:    
        with Session() as session:
            user = session.query(User).filter_by(username=data['username']).first()
            if user:
                return jsonify({
            "success": False,
            "message": "Username already exists"}), 400
            
            email = session.query(User).filter_by(email=data['email']).first()
            if email:
                return jsonify({
            "success": False,
            "message": "Email already exists"}), 400
            
            New_user = User(firstname = data['firstname'], lastname=data['lastname'], username=data['username'], email=data['email'], role=data['role'], gender=data['gender'], phone_number=data['phone_number'])
            New_user.set_password(data['password'])
            
            session.add(New_user)
            session.commit()
            
            add_address = AddressLocation(user_id=New_user.id, address=data['address'])
            session.add(add_address)
            session.commit()
            
            secret_question = SecretQuestion(user_id=New_user.id, question_id=data['question'], answer=data['answer'])
            session.add(secret_question)
            session.commit()
            
            avatar_img = request.files['image']
            if not avatar_img:
                return jsonify({
                    "success": False,
                    "message": "Error: No image file uploaded"}), 400
                
            if avatar_img.filename is not None:
                filename = secure_filename(avatar_img.filename)
                save_path = 'static/images/avatar/' + filename
                avatar_img.save(save_path)
            mime_type = avatar_img.mimetype
            img_data = avatar_img.read()
            
            add_avatar = AvatarImg(user_id=New_user.id, img=img_data, name=filename, mime_type=mime_type)
            session.add(add_avatar)
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
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
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
    
    if 'username' not in data or 'password' not in data:
        return jsonify({
            "success": False,
            "message": "Missing required fields"}),400
    
    with Session() as session:
        try:
            user = session.query(User).filter_by(username=data['username']).first()
            session.execute(text('SELECT * FROM user where username = username and password = password'), {
                'username': data['username'],
                'password': data['password']
            })
            if user and user.check_password(data['password']):
                expires = datetime.timedelta(minutes=60)
                access_token = create_access_token(identity={
                    'id': user.id,
                    'username': user.username,
                }, expires_delta=expires)
                return jsonify({
                    'success' : True,
                    'message': f'User {user.username} logged in successfully',
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
    
    if 'username' not in data:
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
            user = session.query(User).filter_by(username=data['username']).first()
            
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
            user = session.query(User).filter_by(username=data['username']).first()
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
       


        
          