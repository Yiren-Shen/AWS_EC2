from flask import Flask

webapp = Flask(__name__)

from app import main
from app import image
from app import users
from app import load_test