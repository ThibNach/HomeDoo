from flask import Flask, jsonify,send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from pathlib import Path

from registry import register_addons
from config import get_config
from database import create_db_if_not_exists

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    return jsonify({"success": False, "error": str(e)}), code


@app.route("/modules", methods=["GET"])
def get_modules():
    return jsonify(loaded_addons)

ADDONS_DIR = Path(__file__).parent.parent.parent / "addons"

@app.route("/addons/<module>/<path:filename>")
def serve_addon_file(module, filename):
    return send_from_directory(ADDONS_DIR / module / "frontend", filename)


if __name__ == "__main__":
    create_db_if_not_exists()
    global loaded_addons
    loaded_addons = register_addons(app)
    app.run(host="0.0.0.0", port=int(get_config().FLASK_PORT), debug=True)