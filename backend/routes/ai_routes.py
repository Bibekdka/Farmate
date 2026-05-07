import os
import google.generativeai as genai

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

ai_routes = Blueprint("ai_routes", __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per day", "20 per hour"]
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Fallback to check if it's in a different env variable or just warn
    print("WARNING: GEMINI_API_KEY missing in routes/ai_routes.py")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


@ai_routes.route("/api/ai", methods=["POST"])
@limiter.limit("10/minute")
def ai_chat():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Missing request body"
            }), 400

        prompt = data.get("message")

        if not prompt:
            return jsonify({
                "error": "Message is required"
            }), 400

        if len(prompt) > 5000:
            return jsonify({
                "error": "Message too long"
            }), 400

        response = model.generate_content(prompt)

        return jsonify({
            "response": response.text
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
