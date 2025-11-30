from flask import jsonify, request, current_app
from functools import wraps
import requests


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        '''print(f"🔍 Auth header: {auth_header}")  # DEBUG'''

        if not auth_header:
            return jsonify({'error': 'Missing authentication token'}), 401

        token = auth_header.replace('Bearer ', '')
        '''print(f"🔍 Token: {token[:20]}...")  # DEBUG (tylko początek)'''

        try:
            response = requests.post(
                f'{current_app.config["AUTH_SERVICE_URL"]}/auth/verify',
                headers={'Authorization': f'Bearer{token}'},
                timeout=5
            )
            '''print(f"🔍 Auth service response: {response.status_code}") #DEBUG
            print(f"🔍 Response body: {response.json()}")  # DEBUG'''

            if response.status_code != 200:
                return jsonify({'error': 'Invalid authentication token'}), 401

            user_data = response.json().get('user')
            '''print(f"🔍 User data: {user_data}")  # DEBUG'''
            request.user = user_data
            return f(*args, **kwargs)
        except Exception as e:
            print(f'❌ Auth verification error: {e}')
            return jsonify({
                'error': 'Authentication service unavailable'
                }), 503

    return decorated_function
