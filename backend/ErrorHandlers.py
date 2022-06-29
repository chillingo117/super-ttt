from flask import *

errorHandlers = Blueprint("errorHandlers", __name__)


@errorHandlers.errorhandler(404)
def not_found(e):
    return "Error: " + e, 404


@errorHandlers.errorhandler(400)
def bad_request(e):
    return "Error: " + e, 400


@errorHandlers.errorhandler(500)
def insufficient_resources(e):
    return "Error: " + e, 500
