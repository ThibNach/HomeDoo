
def setup(app):
    from .router import router
    app.register_blueprint(router)