from .router import router

def setup(app):
    app.register_blueprint(router)