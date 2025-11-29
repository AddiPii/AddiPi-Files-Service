from flask import Blueprint

files_bp = Blueprint

files_bp.route('/upload', methods=['POST'])()

files_bp.route('/recent', methods=['GET'])()
