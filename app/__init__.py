from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_misaka import Misaka
from flask_cors import CORS
import logging

import os, sys

app = Flask(__name__)
app.run(threaded=True)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
markdown = Misaka().init_app(app)

from app import routes
