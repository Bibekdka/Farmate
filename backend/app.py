import os
import logging
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Add parent directory to path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db

load_dotenv()

migrate = Migrate()


def create_app():
    # Set template and static folders to root for compatibility with existing admin templates
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')

    # =========================
    # REQUIRED ENV VARIABLES
    # =========================

    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

    if not SECRET_KEY:
        SECRET_KEY = "dev-secret-key" # Fallback for local
        print("WARNING: SECRET_KEY missing, using dev default")

    if not DATABASE_URL:
        # Fallback to local SQLite if no remote DB is set
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'farm_data.db')
        DATABASE_URL = f"sqlite:///{db_path}"
        print(f"WARNING: DATABASE_URL missing, using local SQLite: {DATABASE_URL}")

    if not FRONTEND_URL:
        FRONTEND_URL = "http://localhost:5173"
        print("WARNING: FRONTEND_URL missing, using localhost default")

    # =========================
    # APP CONFIG
    # =========================

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # =========================
    # REVERSE PROXY FIX
    # =========================

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # =========================
    # CORS
    # =========================

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [FRONTEND_URL]
            },
            r"/admin/*": {
                "origins": [FRONTEND_URL]
            }
        },
        supports_credentials=True
    )

    # =========================
    # DATABASE
    # =========================

    db.init_app(app)
    migrate.init_app(app, db)

    # =========================
    # LOGGING
    # =========================

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    # =========================
    # HEALTH CHECK
    # =========================

    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "farmate-backend"
        }), 200

    # =========================
    # REGISTER ROUTES
    # =========================

    from backend.routes.ai_routes import ai_routes
    from backend.routes.admin import admin_routes

    app.register_blueprint(ai_routes)
    app.register_blueprint(admin_routes)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
