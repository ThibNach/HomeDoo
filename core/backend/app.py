from flask import Flask

from registry import register_addons
from config import config
from database import create_db_if_not_exists

app = Flask(__name__)

if __name__ == "__main__":
    create_db_if_not_exists()
    register_addons(app)
    app.run(host="0.0.0.0", port=int(config.FLASK_PORT), debug=True)