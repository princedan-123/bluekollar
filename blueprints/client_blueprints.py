"""Client blueprint that contains endpoints without authentication."""
from flask import Blueprint, current_app, request, jsonify
from pymongo.errors import PyMongoError
from models.client import Client

create_client = Blueprint('create_client', __name__)
@create_client.route('/create_client', methods=['POST'], strict_slashes=False)
def create_client_route():
    """An endpoint that creates a new client in the database."""
    json_payload = request.get_json()
    if not json_payload:
        return jsonify({"error": "no json payload"}), 400
    try:
        client = Client(**json_payload)
        data = client.__dict__
        print(f'this is data to be inserted {data}')
        mongo = current_app.extensions['pymongo']
        print(f'this is mongo instance {mongo}')
        insert_result = mongo.db.client.insert_one(data)
        if insert_result.inserted_id:
            return jsonify({'success': f'Client {client.first_name} {client.last_name} created'}), 200
    except ValueError as error:
        error = str(error)
        return jsonify({'error': error}), 400
    except Exception as error:
        error = str(error)
        return jsonify({'error': error}), 500
