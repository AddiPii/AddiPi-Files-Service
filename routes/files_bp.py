from flask import Blueprint
from controllers.files_controller import upload_file, recent_files

files_bp = Blueprint

files_bp.route('/upload', methods=['POST'])(upload_file)

files_bp.route('/recent', methods=['GET'])(recent_files)
