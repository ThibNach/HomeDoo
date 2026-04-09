from .router import router
from .database import init_db


def setup(app):
    app.register_blueprint(router)
    init_db()
