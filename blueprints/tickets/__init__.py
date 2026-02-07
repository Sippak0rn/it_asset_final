from flask import Blueprint

tickets_bp = Blueprint("tickets", __name__)

from . import routes
from .routes import tickets_bp
