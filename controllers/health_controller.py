from flask import jsonify


def health():
    return jsonify({'status': 'ok'}), 200


def index():
    return jsonify({'message': 'AddiPi Files Service is running.'}), 200
