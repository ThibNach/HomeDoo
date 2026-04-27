import bcrypt

from flask import Blueprint, request, jsonify

from core.backend import database, handle_error

router = Blueprint("auth", __name__)


@router.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    password = data["password"].encode("utf-8")
    del data["password"]
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8")
    data["password_hash"] = password_hash

    try:
        database.insert_item("auth_users", data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    else:
        return jsonify({"success": True, "message": "User created"}), 201


@router.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"success ": False, "error": "Missing required fields"}), 400

    try:
        stored_user = database.fetch_where("auth_users", {"username": data.get("username")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

    if len(stored_user) < 1 or not bcrypt.checkpw(data.get("password").encode("utf-8"),
                                                  stored_user[0].get("password_hash").encode("utf-8")):
        return jsonify({"success": False, "message": "Can't find user with this username and password association"})

    return jsonify(
        {"success": True, "message": f"Logged as {data.get("username")}"})  # TODO: real user loging and loading    


@router.route("/auth/users", methods=["GET"])
def get_users():
    return jsonify(database.fetch_all("auth_users"))
