import os
from flask import Flask


basedir = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER = 'files to send'
UPLOAD_FOLDER = 'uploads'
COMPLETED_FOLDER = 'completed'
server_url = 'http://localhost:85/'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images_and_tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['COMPLETED_FOLDER'] = COMPLETED_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 30*1024*1024
