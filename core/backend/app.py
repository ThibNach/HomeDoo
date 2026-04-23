from flask import Flask, jsonify,send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from pathlib import Path

from registry import Registry
from config import config
from database import database

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
    database.create_db_if_not_exists()
    global loaded_addons
    loaded_addons = Registry().register_addons(app)
    app.run(host="0.0.0.0", port=int(config.FLASK_PORT), debug=True)