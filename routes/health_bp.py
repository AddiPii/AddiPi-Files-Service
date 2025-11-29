from flask import Blueprint
from controllers.health_controller import health, index


health_bp = Blueprint('health', __name__)

health_bp.route('/health', methods=['GET'])(health)

health_bp.route('/', methods=['GET'])(index)
