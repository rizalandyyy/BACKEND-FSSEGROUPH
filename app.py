from flask import Flask, jsonify
from flask_migrate import Migrate
from connectors.db import engine, Base
from controllers.user_controller import userBp
from controllers.master_question_controller import masterBp
from controllers.product_controller import productBp
from flask_jwt_extended import JWTManager
from models import *
from flask_cors import CORS

Base.metadata.create_all(engine)


app = Flask (__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
# cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(userBp)
app.register_blueprint(masterBp)
app.register_blueprint(productBp)
jwt = JWTManager(app)
app.config['SECRET_KEY'] = "secret!"

@app.route('/')
def home():
    return jsonify({
        'status': 'LIVE'
    })
