# AddiPi Files Service
from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient
from werkzeug.utils import secure_filename
import os
import json
import time
from datetime import datetime


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


MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 50 * 1024 * 1024))
_allowed = os.getenv('ALLOWED_EXTENSIONS', '.gcode')
ALLOWED_EXTENSIONS = {
    e.strip().lower()
    for e in _allowed.split(',')
    if e.strip()
}
STRICT_CONTENT_CHECK = os.getenv('STRICT_CONTENT_CHECK', '0') == '1'

STORAGE_CONN = os.getenv('STORAGE_CONN')
SERVICE_BUS_CONN = os.getenv('SERVICE_BUS_CONN')
PORT = os.getenv('FILES_PORT')

if not PORT:
    PORT = 5000

if not STORAGE_CONN:
    raise ValueError("STORAGE_CONN environment variable is not set.")
else:
    try:
        blob_client = BlobServiceClient.from_connection_string(STORAGE_CONN)
    except Exception as e:
        raise ConnectionRefusedError(
            f'Failed to connect to Azure Blob Storage: {e}')

sb_client = None
if not SERVICE_BUS_CONN:
    print("SERVICE_BUS_CONN not set — Service Bus messaging will be disabled.")
else:
    try:
        sb_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONN)
    except Exception as e:
        print(f'Failed to create ServiceBusClient (AMQP): {e}')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No File'}), 400

    file = request.files['file']
    original_filename = secure_filename(file.filename or '')
    if not original_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        resp = {
            'error': 'invalid_file_type',
            'allowed': list(ALLOWED_EXTENSIONS),
        }
        return jsonify(resp), 400
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{original_filename}"

    print(f'UPLOADING {original_filename} as {filename}')

    try:
        file_bytes = file.read()
        size = len(file_bytes)
        if size == 0:
            return jsonify({'error': 'empty_file'}), 400
        if size > MAX_UPLOAD_SIZE:
            resp = {'error': 'file_too_large', 'max_bytes': MAX_UPLOAD_SIZE}
            return jsonify(resp), 413

        if STRICT_CONTENT_CHECK:
            try:
                head = file_bytes[:512].decode('utf-8', errors='ignore')
            except Exception:
                head = ''
            if not any(ch in head for ch in ['G', 'M', 'g', 'm']):
                resp = {'error': 'invalid_file_content'}
                return jsonify(resp), 400

        container_client = blob_client.get_container_client('gcode')
        if not container_client.exists():
            container_client.create_container()

        blob = container_client.get_blob_client(filename)
        blob.upload_blob(file_bytes, overwrite=True)
        print(f'UPLOADED {original_filename} as {filename} to Blob Container')

        message = {
            'event': 'file_uploaded',
            'fileId': filename,
            'originalFileName': original_filename,
            'timestamp': str(time.time()),
            'scheduledAt': request.form.get('scheduledAt')
        }

        with sb_client:
            sender = sb_client.get_queue_sender(queue_name='print-queue')
            sender.send_messages([{'body': json.dumps(message)}])

        print(
            f'UPLOADED {original_filename} as {filename} to Service Bus Queue'
            )
        return jsonify({'status': 'success', 'fileId': filename}), 200

    except Exception as e:
        print(f'ERROR uploading {original_filename}: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'AddiPi Files Service is running.'}), 200


@app.route('/files/recent', methods=['GET'])
def recent_files():
    try:
        container_client = blob_client.get_container_client('gcode')
    except Exception as e:
        print(f'ERROR accessing container client: {e}')
        return jsonify({'error': 'storage_unavailable'}), 503

    try:
        if not container_client.exists():
            # No container -> no files
            return jsonify({'files': []}), 200

        blobs = list(container_client.list_blobs())
        # sort by last_modified (newest first)
        blobs_sorted = sorted(
            blobs, key=lambda b: getattr(
                b, 'last_modified', None
                ) or datetime.min, reverse=True
        )

        recent = []
        for b in blobs_sorted[:10]:
            recent.append({
                'fileId': b.name,
                'last_modified': b.last_modified.isoformat() if getattr(
                    b, 'last_modified', None
                    ) else None,
                'size': getattr(b, 'size', None)
            })

        return jsonify({'files': recent}), 200

    except Exception as e:
        print(f'ERROR listing recent files: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    print("AddiPi Files Service starting...")
    app.run(host='0.0.0.0', port=PORT, debug=True)
