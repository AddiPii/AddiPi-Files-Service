# AddiPi Files Service
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from config.config import init_config
from routes.files_bp import files_bp


app = Flask(__name__)

long_origin = (
    "http://addipi-files."
    "b3aaefdfe9dzdea0.swedencentral.azurecontainer.io:5000"
)

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            long_origin,
        ]
    }
})

init_config(app)


app.register_blueprint(files_bp, url_prefix='/files')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'AddiPi Files Service is running.'}), 200


@app.route('/files/recent', methods=['GET'])



if __name__ == "__main__":
    print("AddiPi Files Service starting...")
    app.run(host='0.0.0.0', port=PORT, debug=True)
