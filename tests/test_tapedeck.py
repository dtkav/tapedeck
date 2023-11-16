import json
import pytest
from tapedeck import app

import requests_mock
import pytest


@pytest.fixture
def mock_upstream():
    with requests_mock.Mocker() as m:
        m.get("http://example.com/test", text="response from GET /test")
        m.post("http://example.com/test", json={"response": "from POST /test"}, headers={'Content-Type': 'application/json'})
        # Add more mocked endpoints as needed
        yield m


@pytest.fixture
def client(mock_upstream):
    app.config["UPSTREAM_URL"] = "http://example.com"
    with app.test_client() as client:
        yield client


def test_proxy_get_request(client):
    response = client.get("/test")
    assert response.status_code == 200


def test_proxy_post_request(client):
    headers = {"Content-Type": "application/json"}
    data = {"key": "value"}
    response = client.post("/test", headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    expected_response = {"response": "from POST /test"}
    assert response.json == expected_response


def test_history_endpoint(client):
    client.get("/test")  # Make a request to add to history
    response = client.get("/history")
    assert response.status_code == 200
    history = response.json
    assert len(history) > 0
    assert history[-1]["path"] == "test"


def test_replay_endpoint(client):
    client.get("/test")  # Make a request to add to history
    history_response = client.get("/history")
    history = history_response.json
    last_index = len(history) - 1
    replay_response = client.post("/replay", json={"index": last_index})
    assert replay_response.status_code == 200
