from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

API_KEY = 'YOUR_GEMINI_API_KEY'

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/api/ai', methods=['POST'])
def ai_chat():
    data = request.json

    prompt = data.get('message')

    response = model.generate_content(prompt)

    return jsonify({
        'response': response.text
    })

if __name__ == '__main__':
    app.run(debug=True)
