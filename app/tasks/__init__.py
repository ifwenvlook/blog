#encoding:utf-8
from flask import Blueprint

tasks = Blueprint('tasks', __name__)

from . import celerymail