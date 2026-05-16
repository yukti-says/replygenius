"""
ReplyGenius – Flask Backend
===========================
Entry point. Registers routes and starts the dev server.
"""

from flask import Flask
from flask_cors import CORS
from routes.generate import generate_bp
from routes.health import health_bp
import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env file

def create_app():
    app = Flask(__name__)

    # Allow requests from the browser extension (chrome-extension://)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register route blueprints
    app.register_blueprint(generate_bp)
    app.register_blueprint(health_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print(f"🚀 ReplyGenius backend running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
