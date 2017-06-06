from flask import Blueprint

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
import forms, views