from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from the parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')

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
    app.run(debug=True, use_reloader=False)
