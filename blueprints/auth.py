from flask import Blueprint
from flask import g, session, request, jsonify
import bcrypt

auth = Blueprint('auth', __name__)
@auth.route('/login/<user_type>', methods=['POST'])
def login(user_type):
    """A route that implements login feature for users."""
    try:
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