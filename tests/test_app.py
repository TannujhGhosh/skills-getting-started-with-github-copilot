import copy
import pytest
from fastapi.testclient import TestClient

from src import app


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state for each test so tests are isolated."""
    original = copy.deepcopy(app.activities)
    yield
    app.activities = original


@pytest.fixture
def client():
    return TestClient(app.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure not already present
    assert email not in app.activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app.activities[activity]["participants"]

    # Signing up again should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # Unregister
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in app.activities[activity]["participants"]

    # Unregistering again should return 404
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404


def test_activity_not_found(client):
    resp = client.post("/activities/NonExistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
    resp = client.post("/activities/NonExistent/unregister", params={"email": "a@b.com"})
    assert resp.status_code == 404
