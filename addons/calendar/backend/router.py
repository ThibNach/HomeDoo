from flask import Blueprint

from core.backend import fetch_all

router = Blueprint("calendar", __name__)

@router.route("/calendar/hello")
def hello():
    return "Hello World!"

@router.route("/calendar/entries", methods=["GET"])
def get_calendar_entries():
     return fetch_all("calender_entries")