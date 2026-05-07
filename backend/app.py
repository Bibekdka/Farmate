import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from backend.database import db, migrate

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from backend.routes.ai import ai_routes
from backend.routes.admin import admin_routes

def create_app():
    # Set template and static folders to root for compatibility with existing admin templates
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    CORS(app)

    # Database Configuration
    # Use Render's DATABASE_URL if available, otherwise local SQLite
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # Fallback to local SQLite if no remote DB is set
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'farm_data.db')
        db_url = f"sqlite:///{db_path}"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(ai_routes)
    app.register_blueprint(admin_routes)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

