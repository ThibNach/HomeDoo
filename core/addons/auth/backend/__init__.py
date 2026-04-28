from .router import router
from .tokens.utils import login_required

def setup(app):
    app.register_blueprint(router)

__all__ = ["login_required", "setup"]