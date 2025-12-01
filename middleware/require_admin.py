from functools import wraps
from require_auth import require_auth
from flask import request, jsonify


def require_admin(f):
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function
