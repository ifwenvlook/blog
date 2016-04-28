from flask import Blueprint

auth = Blueprint('tasks', __name__)

from . import celerymail