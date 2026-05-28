from fastapi.testclient import TestClient

from app.core import config
from app.main import create_app


def test_create_app_enables_configured_cors_origin(monkeypatch) -> None:
    monkeypatch.setattr(config.settings, "cors_allowed_origins", "https://app.example.com")
    client = TestClient(create_app())

    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://app.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://app.example.com"
