from flask import Blueprint, jsonify
from models.user_models.master_question import MasterQuestion
from connectors.db import Session


masterBp = Blueprint('masterBp',__name__)

@masterBp.route('/masterquestion', methods=['GET'])
def masterquestion():
    try:
        with Session() as session:
            masterquestions = session.query(MasterQuestion).all()
            masterquestions_list = [
                {'id': mq.id, 'question': mq.question}
                for mq in masterquestions
            ]

            return jsonify({
            "success": True,
            "message": "Master questions retrieved successfully",
            "data": masterquestions_list}), 200
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Error retrieving master questions",
            "data": {"error": str(e)}
        }), 500
