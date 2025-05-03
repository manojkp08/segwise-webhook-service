import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.db.session import SessionLocal
from src.core.models.subscription import Subscription

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = SessionLocal()
    yield db
    db.close()

def test_create_subscription(test_db):
    response = client.post(
        "/api/v1/subscriptions/",
        json={"target_url": "https://example.com/webhook", "secret": "test123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://example.com/webhook"
    assert "id" in data