from flask import Blueprint, request, jsonify
from backend.ai.gemini_service import ai_service

ai_routes = Blueprint('ai_routes', __name__)

@ai_routes.route('/api/ai', methods=['POST'])
def ai_chat():
    data = request.json
    prompt = data.get('message', '')
    
    if not prompt:
        return jsonify({'error': 'Message is required'}), 400

    response_text = ai_service.generate_farming_advice(prompt)

    return jsonify({
        'response': response_text
    })
