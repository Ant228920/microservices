import os

from fastapi.testclient import TestClient

os.environ["USER_SERVICE_URL"] = "http://fake-user-service"
os.environ["PAYMENT_SERVICE_URL"] = "http://fake-payment-service"

from main import app

client = TestClient(app)


def test_payment_details_unauthorized():

    response = client.get("/payment-details/1")

    assert response.status_code == 401