from flask import Blueprint, request, jsonify

from .tokens.utils import login_required
from core.addons.auth.backend.repository import auth_repository

router = Blueprint("auth", __name__)


@router.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        auth_repository.create_person_with_account(data.get("name"), data.get("email"), data.get("password"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    else:
        return jsonify({"success": True, "message": "User created"}), 201

@router.route("/auth/create_person", methods=["POST"])
@login_required
def create_person():
    data = request.get_json()

    if not data.get("name"):
        return jsonify({"success": False, "error": "Missing name to create person"}), 400

    try:
        auth_repository.create_person(data.get("name"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    else:
        return jsonify({"success": True, "message": "Person created"}), 201

@router.route("/auth/delete_person", methods=["POST"])
@login_required
def delete_person():
    data = request.get_json()
    person_id = data.get("id")
    if not person_id:
        return jsonify({"success": False, "error": "Missing id"}), 400

    auth_repository.delete_person(person_id)
    return jsonify({"success": True, "message": "Person deleted"})


@router.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("password") or not data.get("email"):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        result = auth_repository.login(data.get("email"), data.get("password"))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    if not result:
        return jsonify({"success": False, "error": "No combination with email and password found"}), 400

    return jsonify({"success": True, "token": result["token"], "person": result["person"]})

@router.route("/auth/persons", methods=["GET"])
@login_required
def get_persons():
    return jsonify(auth_repository.get_persons())
