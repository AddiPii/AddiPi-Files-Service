import os
from azure.storage.blob import BlobServiceClient
from azure.servicebus import ServiceBusClient


def init_config(app):
    app.config['MAX_UPLOAD_SIZE'] = int(
        os.getenv('MAX_UPLOAD_SIZE', 50 * 1024 * 1024))

    _allowed = os.getenv('ALLOWED_EXTENSIONS', '.gcode')

    app.config['ALLOWED_EXTENSIONS'] = {
        e.strip().lower()
        for e in _allowed.split(',')
        if e.strip()
    }

    app.config['STRICT_CONTENT_CHECK'] = os.getenv(
        'STRICT_CONTENT_CHECK', '0') == '1'

    storage_conn = os.getenv('STORAGE_CONN')
    if not storage_conn:
        raise ValueError("STORAGE_CONN environment variable is not set.")
    try:
        blob_client = BlobServiceClient.from_connection_string(storage_conn)
        app.config['BLOB_CLIENT'] = blob_client
        print("✓ Azure Blob Storage client initialized")
    except Exception as e:
        raise ConnectionRefusedError(
            f'Failed to connect to Azure Blob Storage: {e}'
        )

    service_bus_conn = os.getenv('SERVICE_BUS_CONN')
    if not service_bus_conn:
        print(
            "⚠ SERVICE_BUS_CONN not set — Service Bus messaging will "
            "be disabled."
        )
        app.config['SERVICE_BUS_CLIENT'] = None
    else:
        try:
            sb_client = ServiceBusClient.from_connection_string(
                service_bus_conn)
            app.config['SERVICE_BUS_CLIENT'] = sb_client
            print("✓ Azure Service Bus client initialized")
        except Exception as e:
            print(f'⚠ Failed to create ServiceBusClient (AMQP): {e}')
            app.config['SERVICE_BUS_CLIENT'] = None

    app.config['PORT'] = int(os.getenv('FILES_PORT', 5000))
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL')
    if not app.config['AUTH_SERVICE_URL']:
        print('AUTH_SERVICE_URL not set')

    return app
