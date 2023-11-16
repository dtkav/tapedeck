from flask import Flask, request, jsonify, Response
import requests
import json
from urllib.parse import urljoin
import threading

app = Flask(__name__)
request_history = []

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def proxy(path):
    global request_history
    full_url = urljoin(UPSTREAM_URL, path)
    headers = {k: v for k, v in request.headers.items() if k != 'Host'}
    resp = requests.request(
        method=request.method,
        url=full_url,
        headers=headers,
        json=request.get_json(silent=True),
        data=request.data
    )
    request_history.append({
        'method': request.method,
        'path': path,
        'headers': headers,
        'data': request.data.decode('utf-8'),
        'json': request.get_json(silent=True)
    })
    return (resp.content, resp.status_code, resp.headers.items())

@app.route('/history', methods=['GET'])
def history():
    return jsonify(request_history[-10:])  # Return the last 10 requests

@app.route('/replay', methods=['POST'])
def replay():
    data = request.get_json()
    index = data.get('index')
    if index is not None and index < len(request_history):
        req_to_replay = request_history[index]
        response = requests.request(
            method=req_to_replay['method'],
            url=urljoin(UPSTREAM_URL, req_to_replay['path']),
            headers=req_to_replay['headers'],
            json=req_to_replay['json'],
            data=req_to_replay['data']
        )
        return (response.content, response.status_code, response.headers.items())
    else:
        return jsonify({"error": "Invalid request index"}), 400

import click

# Remove the UPSTREAM_URL constant as it will be passed as an argument

@click.command()
@click.argument('upstream_url', required=True)
def run_server(upstream_url):
    """Start the proxy server with the given UPSTREAM_URL."""
    global UPSTREAM_URL
    UPSTREAM_URL = upstream_url
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

if __name__ == '__main__':
    run_server()

