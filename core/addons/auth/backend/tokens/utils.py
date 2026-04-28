from functools import wraps
from flask import request, jsonify

from .token_manager import token_manager

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"success": False, "error": "Missing token"}), 401

        token = token.replace("Bearer ", "")
        payload = token_manager.verify(token)

        if payload is None:
            return jsonify({"success": False, "error": "Invalid or expired token"}), 401

        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

