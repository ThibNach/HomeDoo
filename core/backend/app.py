from flask import Flask, jsonify,send_from_directory, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from pathlib import Path

from modules import Registry
from config import config
from database import database
from modules.installer import ModuleInstaller

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    return jsonify({"success": False, "error": str(e)}), code


@app.route("/modules", methods=["GET"])
def get_modules():
    return jsonify([
        {k: v for k, v in m.items() if k != "path"}
        for m in loaded_addons
    ])

ADDONS_DIR = Path(__file__).parent.parent.parent / "addons"

@app.route("/addons/<module>/<path:filename>")
def serve_addon_file(module, filename):
    return send_from_directory(ADDONS_DIR / module / "frontend", filename)

@app.route("/modules/install", methods=["POST"])
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

@app.route("/modules/uninstall", methods=["POST"])
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


if __name__ == "__main__":
    database.create_db_if_not_exists()
    database.create_tables_if_not_exist(Path(__file__).parent / "database/schema.json","core")
    global loaded_addons
    loaded_addons = Registry().register_addons(app)
    app.run(host="0.0.0.0", port=int(config.FLASK_PORT), debug=True)