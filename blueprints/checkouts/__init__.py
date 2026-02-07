from flask import Blueprint

checkouts_bp = Blueprint(
    "checkouts",
    __name__,
    url_prefix="/checkouts"
)

from . import routes
