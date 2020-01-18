from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import os

template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'yes-u\\website')

app = Flask(__name__, template_folder=template_dir)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)

from app import routes
