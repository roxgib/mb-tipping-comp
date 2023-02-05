"""Main application file."""

import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import flask_login

with open("../secrets.json") as f:
    _db: dict[str, str] = json.load(f)

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{_db['username']}:{_db['password']}@{_db['server']}:5432/{_db['database']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "BAD_SECRET_KEY"
db = SQLAlchemy(app)
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from . import views, models


login_manager.login_view = "views.login"

with app.app_context():
    db.create_all()
