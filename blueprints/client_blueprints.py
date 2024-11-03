"""A blueprint for client's routes."""
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
    