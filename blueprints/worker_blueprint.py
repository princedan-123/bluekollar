"""A blueprints for worker's routes."""
from flask import Blueprint, request, jsonify, g, session
from models.workers import Worker

worker_routes = Blueprint('worker_routes', __name__)
@worker_routes.route('/create_worker', methods=['POST'], strict_slashes=False)
def create_worker():
    """An endpoint that creates a worker."""
    json_payload = request.get_json()
    if not json_payload:
        return jsonify({' error': 'no json body in the request'}), 400
    try:
        worker = Worker(**json_payload)
        data = worker.__dict__
        #  check if user already exists
        mongo = g.mongo
        exist = mongo.db.worker.find_one({'email': worker.email})
        if exist:
            return jsonify({'error': 'user with this email already exists'})
        #  insert worker into db
        insert_result = mongo.db.worker.insert_one(data)
        if insert_result.inserted_id:
            return jsonify({'successful': f'worker {worker.last_name} created successfully'}), 201
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
    