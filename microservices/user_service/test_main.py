from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

MOCK_SERVICE_PATH = "modules.users.api.routes.UserService"

@patch(MOCK_SERVICE_PATH)
def test_get_user_success(mock_user_service):
    mock_instance = mock_user_service.return_value
    mock_instance.get_user.return_value = {"id": 1, "username": "test_user"}

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1

@patch(MOCK_SERVICE_PATH)
def test_get_user_not_found(mock_user_service):
    mock_instance = mock_user_service.return_value
    mock_instance.get_user.return_value = None

    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}