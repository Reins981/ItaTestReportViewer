import os
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(BASE_PATH, "config", "config.json")

with open(CONFIG_FILE, 'r') as f:
    config_data = json.load(f)
database_path = config_data.get('database_path')

app = Flask(__name__)
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

from app import routes
