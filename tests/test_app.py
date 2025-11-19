import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before/after each test."""
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Math Olympiad"
    test_email = "tester@example.com"

    # Ensure clean start
    assert test_email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{quote(activity)}/signup?email={test_email}")
    assert resp.status_code == 200
    assert test_email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp_dup = client.post(f"/activities/{quote(activity)}/signup?email={test_email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_un = client.post(f"/activities/{quote(activity)}/unregister?email={test_email}")
    assert resp_un.status_code == 200
    assert test_email not in activities[activity]["participants"]

    # Unregistering someone not signed up should return 404
    resp_un2 = client.post(f"/activities/{quote(activity)}/unregister?email=notfound@example.com")
    assert resp_un2.status_code == 404


def test_signup_unknown_activity(client):
    resp = client.post("/activities/Unknown%20Activity/signup?email=a@b.com")
    assert resp.status_code == 404
