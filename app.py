from flask import Flask, jsonify
from connectors.db import engine, Base
from controllers.user_controller import userBp
from controllers.master_question_controller import masterBp
from flask_jwt_extended import JWTManager
from models import *

Base.metadata.create_all(engine)


app = Flask (__name__)
app.register_blueprint(userBp)
app.register_blueprint(masterBp)
jwt = JWTManager(app)
app.config['SECRET_KEY'] = "secret!"

@app.route('/')
def home():
    return jsonify({
        'status': 'LIVE'
    })
