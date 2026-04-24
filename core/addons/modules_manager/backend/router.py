from flask import Blueprint, request, jsonify
from .installer import ModuleInstaller

router = Blueprint("modules_manager", __name__)

@router.route("/modules/install", methods=["POST"])
def install_module():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({ "success" : False, "error" : "Missing URL"}), 400
    try:
        ModuleInstaller().install(url)
        return jsonify({"success": True, "message": "Module installed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@router.route("/modules/uninstall", methods=["POST"])
def uninstall_module():
    data = request.get_json()
    name = data.get("name")
    keep_data = data.get("keep_data")
    if not name:
        return jsonify({"success": False, "error": "Missing name"}), 400
    try:
        ModuleInstaller().uninstall(name, keep_data)
        return jsonify({"success": True, "message": "Module uninstalled"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400