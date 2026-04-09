from flask import Flask

from registry import register_addons
from config import config

app = Flask(__name__)

if __name__ == "__main__":
    register_addons(app)
    app.run(host="0.0.0.0", port=int(config.FLASK_PORT), debug=True)