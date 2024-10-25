from flask import Flask, g
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from os import getenv
from models import client
from blueprints.client_blueprints import client_routes
from uuid import uuid4
load_dotenv()  # loading environment variables from .env file
API_KEY = getenv('API_KEY')
MONGO_URI = getenv('MONGO_URI')
app = Flask(__name__)
secret_key = str(uuid4())
app.config['API_KEY'] = API_KEY
app.config['MONGO_URI'] = MONGO_URI
app.config['SECRET_KEY'] = secret_key
mongo = PyMongo(app)
app.register_blueprint(client_routes, url_prefix='/client')
@app.before_request
def db_setup():
    """A set up function that initializes the mongodb database."""
    g.mongo = mongo

@app.route('/', strict_slashes=False)
def test():
    return '<h1> Welcome to bluekollar </h1>'
app.run(debug=True, port=5000)