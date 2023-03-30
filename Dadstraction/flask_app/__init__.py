from flask import Flask
app = Flask(__name__)
app.secret_key = "this is a secret"

import os
from flask_bcrypt import Bcrypt

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
