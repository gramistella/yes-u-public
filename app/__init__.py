from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_misaka import Misaka
from flask_static_compress import FlaskStaticCompress

app = Flask(__name__)
if __name__ == '__main__':
    app.run(threaded=True)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
markdown = Misaka().init_app(app)
compress = FlaskStaticCompress(app)

from app import routes
