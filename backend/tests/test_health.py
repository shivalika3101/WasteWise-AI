import fastapi.testclient as _testclient
import app.main as _main

client = _testclient.TestClient(_main.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
