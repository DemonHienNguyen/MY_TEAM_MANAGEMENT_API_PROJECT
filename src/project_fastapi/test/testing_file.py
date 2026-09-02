from http import HTTPStatus

from fastapi.testclient import TestClient

from ..app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data["status_code"] == 200
    assert data["message"] == "FastAPI chạy tốt"
    assert data["data"]["message"] == "Không có vấn đề"


def test_login_wrong_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "dungxyz9999@construct.com",
            "password": "skibidi",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    data = response.json()
    assert data["status_code"] == 401
    assert data["error"] == "INVALID_CREDENTIALS_ERROR"