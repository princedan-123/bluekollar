"""Client blueprint that contains endpoints without authentication."""
from flask import Blueprint, request, jsonify, g, session
from models.client import Client
import bcrypt

client_routes = Blueprint('client_routes', __name__)
@client_routes.route('/create_client', methods=['POST'], strict_slashes=False)
def create_client_route():
    """An endpoint that creates a new client in the database."""
    json_payload = request.get_json()
    if not json_payload:
        return jsonify({"error": "no json payload"}), 400
    try:
        client = Client(**json_payload)
        data = client.__dict__
        mongo = g.mongo
        # check if client already exists in databse
        exist = mongo.db['client'].find_one({'email': client.email})
        if exist:
            return jsonify({'error': 'client with this email already exists'}), 400
        insert_result = mongo.db['client'].insert_one(data)
        if insert_result.inserted_id:
            return jsonify({'success': f'Client {client.first_name} {client.last_name} created'}), 201
    except ValueError as error:
        import traceback
        traceback.print_exc()
        error = str(error)
        return jsonify({'error': error}), 400
    except Exception as error:
        import traceback
        traceback.print_exc()
        error = str(error)
        return jsonify({'error': error}), 500


@client_routes.route('/login', methods=['POST'], strict_slashes=False)
def login():
    """A route that logs client in and creates session data."""
    try:
        login_credentials = request.get_json()
        email = login_credentials.get('email')
        password = login_credentials.get('password')
        if email is None:
            return jsonify({ 'error' : 'email field is missing'}), 400
        if password is None:
            return jsonify({ 'error': 'password field is missing'}), 400
        mongo = g.mongo
        user = mongo.db['client'].find_one_or_404({'email': email})
        user_password = user.get('password')
        check_passwd = bcrypt.checkpw(password.encode('utf-8'), user_password)
        if not check_passwd:
            return jsonify({'error': 'password is invalid'}), 400
        # encrypt session data
        last_name = user.get('last_name')
        session['last_name'] = last_name
        session['email'] = email
        return jsonify({'user': 'logged in'}), 200
    except Exception as error:
        import traceback
        traceback.print_exc()
        error = str(error)
        return jsonify({'error': error}), 500

@client_routes.route('/profile', methods=['GET'], strict_slashes=False)
def client_profile():
    """A route that retrieves the client info."""
    # check if user is logged in
    print(session)
    if session.get('last_name') and session.get('email'):
        email = session.get('email')
        mongo = g.mongo
        user = mongo.db['client'].find_one_or_404({'email': email}, {
            'first_name': 1, 'last_name': 1, 'gender': 1, 'age': 1,
            'country': 1, 'state': 1, 'muncipality': 1, 'position': 1,
            'street': 1, '_id': 0
            })
        return jsonify(user), 200
    else:
        return jsonify({'error': 'user not logged in'})