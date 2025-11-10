import os
import sys
import importlib
import io
from types import SimpleNamespace

def make_dummy_blob_client():
    class DummyBlob:
        def __init__(self):
            self._blobs = {}

        def get_container_client(self, name):
            # zwraca obiekt z metodami exists/create_container/get_blob_client/list_blobs
            class Container:
                def __init__(self):
                    self._exists = True
                def exists(self):
                    return True
                def create_container(self):
                    self._exists = True
                def get_blob_client(self, blob_name):
                    class BlobClient:
                        def upload_blob(self, data, overwrite=False):
                            # nic nie robi - mock upload
                            return None
                    return BlobClient()
                def list_blobs(self):
                    return []
            return Container()
    return DummyBlob()

class DummyServiceBus:
    # prosty kontekstowy klient Service Bus z get_queue_sender(...).send_messages(...)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def get_queue_sender(self, queue_name):
        class Sender:
            def send_messages(self, msgs):
                return None
        return Sender()

def test_upload_endpoint(monkeypatch):
    # 1) ustaw env przed importem app
    monkeypatch.setenv('STORAGE_CONN', 'fake-storage-conn')
    # możesz zostawić SERVICE_BUS_CONN pusty lub dać wartość; app znosi brak SB ale my mockujemy
    monkeypatch.setenv('SERVICE_BUS_CONN', 'fake-sb-conn')

    # 2) import app fresh
    if 'app' in sys.modules:
        del sys.modules['app']
    app = importlib.import_module('app')

    # 3) zamockuj blob_client i sb_client tak, by nie robiły zewnętrznych wezwań
    app.blob_client = make_dummy_blob_client()
    app.sb_client = DummyServiceBus()

    # 4) użyj test_client i wyślij multipart z BytesIO
    client = app.app.test_client()
    data = {
        'file': (io.BytesIO(b'G1 X10 Y10\n'), 'test.gcode'),
        'scheduledAt': '2024-01-01T00:00:00Z'
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')

    assert resp.status_code == 200
    body = resp.get_json()
    assert body and body.get('status') == 'success'
    assert 'fileId' in body