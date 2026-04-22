from flask import Blueprint, jsonify, request

from core.backend import Database

router = Blueprint("calendar", __name__)


@router.route("/calendar/entries", methods=["GET"])
def get_calendar_entries():
     return jsonify(Database().fetch_all("calendar_entries"))


@router.route("/calendar/entries", methods=["POST"])
def add_calendar_entry():
    data = request.get_json()
    if not data.get("title") or not data.get("start_datetime"):
        return jsonify({"success": False, "error": "Missing required fields"}), 400    
    Database().insert_item("calendar_entries", data)
    return jsonify({"success": True, "message": "Entry created"}), 201