from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient
import os
import json
from datetime import datetime


app = Flask(__name__)

STORAGE_CONN = os.getenv('STORAGE_CONN')
SERVICE_BUS_CONN = os.getenv('SERVICE_BUS_CONN')

blob_client = BlobServiceClient.from_connection_string(STORAGE_CONN)
sb_client = ServiceBusClient.from_connection_string(SERVICE_BUS_CONN)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No File'}), 400
    
    file = request.files['file']
    original_filename = file.filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{original_filename}"

    print(f'UPLOADING {original_filename} as {filename}')

    try:
        container_client = blob_client.get_container_client('gcode')
        if not container_client.exists():
            container_client.create_container()
        
        blob = container_client.get_blob_client(filename)
        blob.upload_blob(file, overwrite=True)


        message = {
            'event': 'file_uploaded',
            
        }

if __name__ == "__main__":
    print('ok')