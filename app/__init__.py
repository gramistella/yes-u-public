from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_misaka import Misaka
from flask_static_compress import FlaskStaticCompress
from flask_compress import Compress

app = Flask(__name__)
if __name__ == '__main__':
    app.run(threaded=True)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
markdown = Misaka().init_app(app)
flask_static_compress = FlaskStaticCompress(app)
Compress().init_app(app)

from app import routes
