from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import json
import time
from datetime import datetime


def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No File'}), 400

    file = request.files['file']
    original_filename = secure_filename(file.filename or '')
    if not original_filename:
        return jsonify({'error': 'Invalid filename'}), 400

    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()

    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    if ext not in allowed_extensions:
        resp = {
            'error': 'invalid_file_type',
            'allowed': list(allowed_extensions),
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

        max_size = current_app.config['MAX_UPLOAD_SIZE']
        if size > max_size:
            resp = {'error': 'file_too_large', 'max_bytes': max_size}
            return jsonify(resp), 413

        if current_app.config['STRICT_CONTENT_CHECK']:
            try:
                head = file_bytes[:512].decode('utf-8', errors='ignore')
            except Exception:
                head = ''
            if not any(ch in head for ch in ['G', 'M', 'g', 'm']):
                resp = {'error': 'invalid_file_content'}
                return jsonify(resp), 400

        blob_client = current_app.config['BLOB_CLIENT']
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

        sb_client = current_app.config.get('SERVICE_BUS_CLIENT')
        if sb_client:
            with sb_client:
                sender = sb_client.get_queue_sender(queue_name='print-queue')
                sender.send_messages([{'body': json.dumps(message)}])

            print(
                f'UPLOADED {original_filename} as {filename} '
                'to Service Bus Queue'
            )

        return jsonify({'status': 'success', 'fileId': filename}), 200

    except Exception as e:
        print(f'ERROR uploading {original_filename}: {e}')
        return jsonify({'error': str(e)}), 500
