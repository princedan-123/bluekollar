"""A client model that represents the client"""
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt
from os import getenv
from datetime import datetime
load_dotenv()
API_KEY = getenv('API_KEY')
import requests

if not API_KEY:
    raise EnvironmentError('API key not found in the environment variable')
class Client:
    """
    This class creates an instance of the client
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
        street(str): The client's address.
        city_or_town(str): The client's city or town
        muncipality(str): The clients locality.
    """
    mandatory_fields = {
        'first_name': str, 'last_name': str, 'age': int, 'gender': str,
        'country': str, 'state': str, 'street':str, 'muncipality': str,
        'city_or_town': str, 'password':str, 'email': str
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
        if len(kwargs.keys()) != Client.field_count:
            raise ValueError('incorrect number of fields')
        for field, value in kwargs.items():
            if field in Client.mandatory_fields and isinstance(value, Client.mandatory_fields[field]):
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
            self.position = Client.geocode_user(self.country, self.state, self.city_or_town, self.muncipality, self.street)
        except Exception as error:
            raise error
    @staticmethod
    def geocode_user(country, state, city_or_town, muncipality, street):
        """
        Geocodes  client location using an external API.
        Parameters:
            kwargs(dict): Keyword arguments.
        Returns:
            position(dict): The coordinate result from the geocoding.
        """
        # use has attribute to check if instance has the following attributes
        searchText = f'{country} {state} {city_or_town} {street} {muncipality}'
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
    
    @staticmethod
    def validate_location_data(country, state, city_or_town, muncipality, street):
        """
        A static method that validates location data.
        Parameters:
           country(str): The clients country.
           state(str): The state where the client resides.
           city_or_town(str): The client's city or town.
           muncipality(str): The local government area or client's muncipality.
           address(str): The clients address including street name and number. 
        """
        if not isinstance(country, str) and not isinstance(state, str):
            raise ValueError('location data invalid data type')
        if not isinstance(city_or_town, str) and not isinstance(muncipality, str):
            raise ValueError('location data invalid data type')
        if not isinstance(street, str):
            raise ValueError('location data invalid data type')
        return True
