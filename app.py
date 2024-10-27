from flask import Flask, g
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from os import getenv
from models import client
from blueprints.client_blueprints import client_routes
from blueprints.worker_blueprint import worker_routes
from blueprints.auth import auth
from uuid import uuid4
import bcrypt
load_dotenv()  # loading environment variables from .env file
API_KEY = getenv('API_KEY')
MONGO_URI = getenv('MONGO_URI')
app = Flask(__name__)
secret_key = str(uuid4())
app.config['API_KEY'] = API_KEY
app.config['MONGO_URI'] = MONGO_URI
app.config['SECRET_KEY'] = secret_key
mongo = PyMongo(app)
print(auth)
app.register_blueprint(client_routes, url_prefix='/client')
app.register_blueprint(worker_routes, url_prefix='/worker')
app.register_blueprint(auth, url_prefix='/auth')
@app.before_request
def db_setup():
    """A set up function that initializes the mongodb database."""
    g.mongo = mongo

@app.route('/', strict_slashes=False)
def index():
    """A route for the index page."""
    return '<h1> Welcome to bluekollar </h1>'

app.run(debug=True, port=5000)