"""A worker model that represents a worker instance"""
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt
from os import getenv
from datetime import datetime
import requests
load_dotenv()
API_KEY = getenv('API_KEY')

if not API_KEY:
    raise EnvironmentError('API key not found in the environment variable')
class Worker:
    """
    This class creates an instance of the Worker
    Attributes:
        mandatory_fields(dict): a dictionary of mandatory fields the class must have.
        field_count(int): The size of the field.
        first_name(str): The first name of the client.
        last_name(str): The last name of the client.
        email(str): client's email.
        password(str): client's password.
        age(int): The age of the client.
        gender(str): The client's gender.
        country(str): The client's country.
        state(str): The client's state.
        address(str): The client's address.
        city_or_town(str): The client's city or town
        muncipality(str): The clients locality.
        profession(str): The workers profession.

    """
    mandatory_fields = {
        'first_name': str, 'last_name': str, 'age': int, 'gender': str,
        'country': str, 'state': str, 'street':str, 'muncipality': str,
        'city_or_town': str, 'password':str, 'email': str, 'profession': str
        }
    field_count = len(mandatory_fields.keys())
    def __init__(self, **kwargs) -> None:
        """
        Initializes the class
        Parameters:
            self(instance): Instance of the class
            kwargs(dict): keyword arguements
        Returns:
            None
        Raises:
            ValueError: if the keyword argument contains an invalid field or value or incorrect number of fields
        """
        if len(kwargs.keys()) != Worker.field_count:
            raise ValueError('incorrect number of fields')
        for field, value in kwargs.items():
            if field in Worker.mandatory_fields and isinstance(value, Worker.mandatory_fields[field]):
                if field == 'password':
                    value = value.encode('utf-8')
                    hashed_password = hashpw(value, gensalt())
                    value = hashed_password
                    # value = value.decode('utf-8')
                setattr(self, field, value)
            else:
                raise ValueError('invalid field or value')
        self.created_on = str(datetime.today())
        try:
            self.position = Worker.geocode_user(self.country, self.state, self.city_or_town, self.muncipality, self.street)
        except Exception as error:
            raise error
    @staticmethod
    def geocode_user(country, state, city_or_town, muncipality, address):
        """
        Geocodes a worker location using an external API.
        Parameters:
            country(str): the worker's country.
            state(str): the worker's state.
            city_or_town(str): the worker's city or town.
            muncipality(str): the worker's muncipality or local government area.
            street(str): the worker's street name and number.
        Returns:
            position(dict): The coordinate result from the geocoding in latitude and longitutde.
        """
        # use has attribute to check if instance has the following attributes
        searchText = f'{country} {state} {city_or_town} {address} {muncipality}'
        url = f'https://api.tomtom.com/search/2/geocode/{searchText}.json'
        response = requests.get(url, params={'key': API_KEY}, timeout=180)
        try:
            response = response.json()
            results = response.get('results', [])
        except:
            raise Exception('Invalid JSON response from geocoding API')
        if len(results) != 0 :
            results.sort(key=lambda dic : dic['matchConfidence']['score'], reverse=True)
            closestMatch = results[0]
            position = {
                'latitude': closestMatch['position']['lat'],
                'longitude': closestMatch['position']['lon']
                }
            return position
        else:
            raise Exception('geocoding failed please provide a descriptive location')