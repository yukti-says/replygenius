"""
Health check endpoint.
The extension popup pings this to show online/offline status.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "ReplyGenius"}), 200
