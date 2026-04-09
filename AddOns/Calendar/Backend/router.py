from flask import Blueprint

router = Blueprint("Calendar", __name__)

@router.route("/Calendar/hello")
def hello():
    return "Hello World!"