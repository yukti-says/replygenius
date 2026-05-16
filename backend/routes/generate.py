"""
ReplyGenius – /api/generate endpoint
=====================================
Receives post text + tone from the extension,
builds a smart prompt, and calls the AI API.
"""

from flask import Blueprint, request, jsonify
from utils.ai_client import generate_reply
from utils.prompt_builder import build_prompt

generate_bp = Blueprint("generate", __name__)


@generate_bp.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True)

    # ── Validate input ─────────────────────────────────────────
    if not data:
        return jsonify({"error": "No JSON body received."}), 400

    post_text = (data.get("postText") or "").strip()
    tone      = (data.get("tone") or "smart").strip()
    platform  = (data.get("platform") or "unknown").strip()
    length    = (data.get("length") or "Medium").strip()

    if not post_text:
        return jsonify({"error": "postText is required."}), 400

    if len(post_text) > 3000:
        post_text = post_text[:3000]

    # ── Build prompt ───────────────────────────────────────────
    prompt = build_prompt(post_text, tone, platform, length)

    # ── Call AI ────────────────────────────────────────────────
    reply, error = generate_reply(prompt)

    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply}), 200
