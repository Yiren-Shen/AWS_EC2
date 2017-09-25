from flask import Flask

webapp = Flask(__name__)

from app import main
from app import manager
from app import grow_shrink
from app import auto_scaling
from app import delete
