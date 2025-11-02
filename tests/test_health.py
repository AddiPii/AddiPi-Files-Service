import importlib
import sys


def test_health_endpoint():
    # Ensure fresh import
    if 'app' in sys.modules:
        del sys.modules['app']
    app = importlib.import_module('app')

    client = app.app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {'status': 'ok'}
