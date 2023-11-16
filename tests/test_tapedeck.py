import json
import pytest
from tapedeck import app

import requests_mock
import pytest



@pytest.fixture
def mock_upstream():
    with requests_mock.Mocker() as m:
        from urllib.parse import parse_qs

        m.get("http://example.com/test", additional_matcher=lambda req: parse_qs(req.query) == {'param1': ['value1'], 'param2': ['value2']} or req.query == '', text="response from GET /test with or without params", headers={"Content-Type": "application/json", "Server": "MockServer"})
        m.post(
            "http://example.com/test",
            json={"response": "from POST /test"},
            headers={"Content-Type": "application/json"},
        )
        # Add mock responses for PUT, PATCH, DELETE, and POST to /text-plain
        m.put("http://example.com/test", text="response from PUT /test")
        m.patch("http://example.com/test", text="response from PATCH /test")
        m.delete("http://example.com/test", text="response from DELETE /test")
        m.post("http://example.com/text-plain", text="response from POST /text-plain", headers={"Content-Type": "text/plain"})
        yield m

def test_proxy_post_request_text_plain(client, mock_upstream):
    # Send a POST request to the proxy
    headers = {"Content-Type": "text/plain"}
    data = "plain text data"
    response = client.post("/text-plain", headers=headers, data=data)

    # Assert the response status code and content type
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain"
    assert response.data.decode("utf-8") == "response from POST /text-plain"


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


def test_proxy_put_request(client, mock_upstream):
    # Send a PUT request to the proxy
    headers = {"Content-Type": "application/json"}
    data = {"key": "updated value"}
    response = client.put("/test", headers=headers, data=json.dumps(data))

    # Assert the response status code
    assert response.status_code == 200
    # Add additional assertions if the upstream server provides a response body

def test_proxy_patch_request(client, mock_upstream):
    # Send a PATCH request to the proxy
    headers = {"Content-Type": "application/json"}
    data = {"key": "patched value"}
    response = client.patch("/test", headers=headers, data=json.dumps(data))

    # Assert the response status code
    assert response.status_code == 200
    # Add additional assertions if the upstream server provides a response body

def test_proxy_delete_request(client, mock_upstream):
    # Send a DELETE request to the proxy
    response = client.delete("/test")

    # Assert the response status code
    assert response.status_code == 200
    # Add additional assertions if the upstream server provides a response body

def test_proxy_header_preservation(client, mock_upstream):
    # Send a request to the proxy with custom headers
    request_headers = {
        "Custom-Header": "CustomValue",
        "Another-Header": "AnotherValue"
    }
    response = client.get("/test", headers=request_headers)

    # Assert the response status code
    assert response.status_code == 200

    # Assert that the request headers sent to the upstream server are preserved
    assert mock_upstream.last_request.headers["Custom-Header"] == "CustomValue"
    assert mock_upstream.last_request.headers["Another-Header"] == "AnotherValue"

    # Assert that the response headers from the upstream server are preserved
    # (assuming the mock upstream server is set to return specific headers)
    assert response.headers.get("Content-Type") == "application/json"
    assert response.headers.get("Server") == "MockServer"  # Example header

def test_replay_endpoint(client):
    client.get("/test")  # Make a request to add to history
    history_response = client.get("/history")
    history = history_response.json
    last_index = len(history) - 1
    replay_response = client.post("/replay", json={"index": last_index})
    assert replay_response.status_code == 200

def test_proxy_get_with_query_params(client, mock_upstream):
    # Send a GET request with query parameters to the proxy
    query_params = {'param1': 'value1', 'param2': 'value2'}
    response = client.get("/test", query_string=query_params)

    # Assert the response status code
    assert response.status_code == 200
    # Assert the mock server received the correct query parameters
    from urllib.parse import parse_qs
    assert parse_qs(mock_upstream.last_request.query) == parse_qs('param1=value1&param2=value2')
