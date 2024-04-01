import requests
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import *
import json
from app.service.ks_llm_generation import input_query, create_doc_vectors
from app.app_init import app

api_routes = Blueprint('api', __name__)


@api_routes.route('/', methods=['GET'])
def index():
    app.logger.info("Server is running ...")
    return jsonify({"message": "Server is running ..."})


@api_routes.route('/get_query', methods=['POST'])
def get_query():
    query = request.get_json()
    if query:

        result = input_query(query.get('query'))
        return jsonify({'status': 'success', 'response': result})

    else:
        return jsonify({'status': 'failed', 'error': 'Invalid JSON data'})


@api_routes.route('/create_vectors', methods=['POST'])
def create_vectors():
    try:
        result = create_doc_vectors()
        return jsonify({'status': 'success', 'response': result})
    except Exception as e:
        return jsonify({'status': 'failure', 'response':None})


