from flask import jsonify, request, current_app
from functools import wraps
import requests


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authentication token'}), 401

        token = auth_header.replace('Bearer ', '')
        try:
            response = requests.post(
                f'{current_app.config['AUTH_SERVICE_URL']}/auth/verify',
                headers={'Authorization': f'Bearer {token}'},
                timeout=5
            )
            if response.status_code != 200:
                return jsonify({'error': 'Invalid authentication token'}), 401

            user_data = response.json().get('user')
            request.user = user_data
            return f(*args, **kwargs)
        except Exception as e:
            print(f'Auth verification error: {e}')
            return jsonify({
                'error': 'Authentication service unavailable'}), 503

    return decorated_function
