import fastapi.testclient as _testclient

import app.main as _main

client = _testclient.TestClient(_main.app)


def test_preflight_allows_the_frontend_origin():
    response = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
