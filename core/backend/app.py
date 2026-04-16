from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from registry import register_addons
from config import config
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


if __name__ == "__main__":
    create_db_if_not_exists()
    global loaded_addons
    loaded_addons = register_addons(app)
    app.run(host="0.0.0.0", port=int(config.FLASK_PORT), debug=True)