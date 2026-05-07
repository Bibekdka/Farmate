from flask import Flask
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from the current directory (backend/)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from backend.routes.ai import ai_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(ai_routes)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
