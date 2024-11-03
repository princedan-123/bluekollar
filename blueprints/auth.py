from flask import Blueprint
from flask import g, session, request, jsonify
import bcrypt
import requests
import re
import os
from models.client import Client

API_KEY = os.getenv('API_KEY')
auth = Blueprint('auth', __name__)
@auth.route('/login/<user_type>', methods=['POST'])
def login(user_type):
    """A route that implements login feature for users."""
    try:
        if request.content_type == 'application/json':
            login_credentials = request.get_json()
            email = login_credentials.get('email')
            password = login_credentials.get('password')
            if email is None:
                return jsonify({ 'error' : 'email field is missing'}), 400
            if password is None:
                return jsonify({ 'error': 'password field is missing'}), 400
        #  validate user_type
        if user_type not in ['client', 'worker']:
            return jsonify({'error': 'invalid user type'}), 400
        #  database operation
        mongo = g.mongo
        user = mongo.db[user_type].find_one_or_404({'email': email})
        user_password = user.get('password')
        check_passwd = bcrypt.checkpw(password.encode('utf-8'), user_password)
        if not check_passwd:
            return jsonify({'error': 'password is invalid'}), 400    
        #  add user data to session
        last_name = user.get('last_name')
        session['last_name'] = last_name
        session['email'] = email
        session['coordinates'] = user.get('position')
        session['country'] = user.get('country')
        session['state'] = user.get('state')
        session['city_or_town'] = user.get('city_or_town')
        session['muncipality'] = user.get('muncipality')
        session['street'] = user.get('street')
        return jsonify({'user': 'logged in'}), 200
    except Exception as error:
        import traceback
        traceback.print_exc()
        error = str(error)
        return jsonify({'error': error}), 500
    
@auth.route('/profile/<user_type>', methods=['GET'], strict_slashes=False)
def profile(user_type):
    """A route that retrieves a user's info."""
    #  user_type validation
    if user_type not in ['client', 'worker']:
        return jsonify({'error': 'invalid user type'}), 400
    #  check if user is logged in
    if session.get('last_name') and session.get('email'):
        email = session.get('email')
        mongo = g.mongo
        user = mongo.db[user_type].find_one_or_404({'email': email}, {
            'first_name': 1, 'last_name': 1, 'gender': 1, 'age': 1,
            'country': 1, 'state': 1, 'muncipality': 1, 'position': 1,
            'street': 1, '_id': 0
            })
        return jsonify(user), 200
    else:
        return jsonify({'error': 'user not logged in'})
    
@auth.route('/remove/<user_type>', methods=['DELETE'], strict_slashes=False)
def remove_user(user_type):
    """"A routes that deletes a user's account."""
    #  validate user_type
    if user_type not in ['client', 'worker']:
        return jsonify({'error': 'user type invalid'}), 400
    if not session:
        return jsonify({' error': 'user not logged in'})
    payload = request.get_json()
    email = payload.get('email')
    password = payload.get('password')
    if not email:
        return jsonify({ 'error': 'email field is missing.'})
    if not password:
        return jsonify({' error: password field is missing.'})
    #  retrieve database object.
    mongo = g.mongo
    #  check if the user's credentials are valid
    user = mongo.db[user_type].find_one_or_404({'email': email})
    check_password = bcrypt.checkpw(password.encode('utf-8'), user.get('password'))
    if not check_password:
        return jsonify({'error': 'user password is invalid'})
    result = mongo.db[user_type].delete_one({'email': email})
    if result.deleted_count == 1:
        return jsonify({ 'success': 'user removed'}), 400
    return jsonify({ 'error': 'no user removed, check if email is valid'}), 400

@auth.route('/search/<string:profession>', methods=['GET', 'POST'], strict_slashes=False)
def search(profession):
    """A route that searches the nearest worker to a client."""
    client_coordinate = None
    location_data = {}
    try:
        #  get client's coordinates
        if request.content_type == 'application/json':
            location_data = request.get_json()
            is_valid = Client.validate_location_data(**location_data)
            if is_valid:
                #  geocode the location data to get latitude and longitutde
                client_coordinate = Client.geocode_user(**location_data)
        elif session.get('coordinates'):
            #  get the coordinate from session data if user is logged in
            client_coordinate = session.get('coordinates')
            location_data.update(session)
        else:
            return jsonify({'error': 'client location data is missing, or user not logged in'}), 400
        client_matrix = [{'point': {'latitude':client_coordinate['latitude'], 'longitude': client_coordinate['longitude']}}]
        #  get workers' coordinates
        mongo = g.mongo
        country = location_data.get('country')
        state = location_data.get('state')
        city_or_town = location_data.get('city_or_town')
        street = location_data.get('street')
        workers = mongo.db['worker'].find({
            'country': country, 'state': state, 'city_or_town': city_or_town,
            'profession': re.compile(f'{profession}', re.IGNORECASE)
            }, {'password': 0, '_id': 0})
        workers = list(workers)
        #  used list comprenshion to create destination point for api matrix request
        workers_matrix = [{'point': {'latitude': worker['position']['latitude'], 'longitude': worker['position']['longitude']}} for worker in workers]
        api_matrix_request = {
            'origins': client_matrix,
            'destinations': workers_matrix,
            'options': {
                'departAt': 'any',
                'traffic': 'historical'
                }
            }
        api_base_url = 'api.tomtom.com'
        version_number = 2
        response = requests.post(f'https://{api_base_url}/routing/matrix/{version_number}', params={'key': API_KEY }, json=api_matrix_request)
        if response.status_code == 200:
            response_body = response.json()
            #  sort the result in ascending order
            response_body['data'].sort(key=lambda result: result.get('routeSummary').get('lengthInMeters'))
            nearest_workers = []
            for data in response_body['data']:
                index = data.get('destinationIndex')
                nearest_workers.append(workers[index])
            return jsonify({'success': nearest_workers})
        return jsonify({'error': 'an error occured'}), response.status_code
    except ValueError as error:
        error = str(error)
        return jsonify({'error': error}), 400
    except Exception as error:
        error = str(error)
        return jsonify({'error': error}), 500