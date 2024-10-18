from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from os import getenv
from models import client
from blueprints.client_blueprints import create_client
load_dotenv()  # loading environment variables from .env file
API_KEY = getenv('API_KEY')
MONGO_URI = getenv('MONGO_URI')
app = Flask(__name__)
app.config['API_KEY'] = API_KEY
app.config['MONGO_URI'] = MONGO_URI
mongo = PyMongo(app)
print(f'this is main mongo {mongo}')
print(create_client)
app.register_blueprint(create_client, url_prefix='/client')


@app.route('/', strict_slashes=False)
def test():
    return '<h1> Welcome to bluekollar </h1>'
app.run(debug=True, port=5000)