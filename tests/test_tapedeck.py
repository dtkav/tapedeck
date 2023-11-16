import json
import pytest
from tapedeck import app

import requests_mock
import pytest



@pytest.fixture
def mock_upstream(requests_mock):
    def _mock_upstream(mock_data):
        method = mock_data.get('method', 'GET').lower()
        path = mock_data.get('path', '/')
        full_url = f"http://example.com{path}"
        status = mock_data.get('status_code', 200)
        headers = mock_data.get('response_headers', {})
        body = mock_data.get('response_body', '')

        with requests_mock.Mocker() as m:
            m.request(method, full_url, text=body, status_code=status, headers=headers)
            yield m
    return _mock_upstream

        m.get("http://example.com/test", additional_matcher=lambda req: parse_qs(req.query) == {'param1': ['value1'], 'param2': ['value2']} or req.query == '', text='{"response": "from GET /test with or without params"}', headers={"Content-Type": "application/json", "Server": "MockServer"})
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


import base64

def test_history_endpoint(client):
    # Make a few requests to add to history
    for _ in range(15):
        client.get("/test")
    
    # Fetch the first page of history
    response = client.get("/history")
    assert response.status_code == 200
    first_page = response.json
    assert len(first_page['history']) > 0
    # Check if any entry in the first page of history has the path "test"
    assert any(entry["path"] == "test" for entry in first_page['history'])
    
    # Fetch the next page using the 'next' cursor
    next_cursor = first_page['next']
    response = client.get(f"/history?after={next_cursor}")
    assert response.status_code == 200
    second_page = response.json
    assert len(second_page['history']) > 0
    assert second_page['history'][0]["path"] == "test"
    
    # Ensure the 'previous' cursor points to the first page
    prev_cursor = second_page['previous']
    response = client.get(f"/history?before={prev_cursor}")
    assert response.status_code == 200
    previous_page = response.json
    assert len(previous_page['history']) > 0
    assert previous_page['history'][0]["path"] == "test"


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

def test_proxy_http_status_storage(client, mock_upstream):
    # Send a GET request to the proxy
    response = client.get("/test")
    assert response.status_code == 200

    # Fetch the history
    history_response = client.get("/history")
    assert history_response.status_code == 200
    history = history_response.json['history']

    # Check if the status code, response headers, and response body are stored in the history
    assert 'status_code' in history[0]
    assert history[0]['status_code'] == 200
    assert 'response_headers' in history[0]
    assert 'Content-Type' in history[0]['response_headers']
    assert history[0]['response_headers']['Content-Type'] == 'application/json'
    assert 'response_body' in history[0]
    assert 'response from GET /test with or without params' in history[0]['response_body']

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
