from flask import Blueprint

router = Blueprint("calendar", __name__)

@router.route("/calendar/hello")
def hello():
    return "Hello World!"