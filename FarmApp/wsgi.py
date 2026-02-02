import os
from app import app, db

# Ensure tables are created in production (Render)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
