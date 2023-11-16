from flask import Flask, request, jsonify, Response
import requests
from urllib.parse import urljoin

from history import HistoryManager

app = Flask(__name__)
history_manager = HistoryManager()


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def proxy(path):
    global request_history
    full_url = urljoin(app.config["UPSTREAM_URL"], path)
    headers = {k: v for k, v in request.headers.items() if k != "Host"}
    resp = requests.request(
        method=request.method,
        url=full_url,
        headers=headers,
        json=request.get_json(silent=True),
        data=request.data,
        params=request.args,  # Forward the query parameters
    )

    response_headers = {k: v for k, v in resp.headers.items()}
    from history import HistoryEntry  # Ensure this import is at the top of the file

    history_entry = HistoryEntry(
        method=request.method,
        path=path,
        status_code=resp.status_code,
        headers=headers,
        data=request.data.decode("utf-8"),
        response_headers=response_headers,
        response_body=resp.text,
    )
    request_history.append(history_entry)
    save_history_to_file()
    # Ensure the response has the correct content type for JSON responses
    response_headers = dict(resp.headers)
    return (resp.content, resp.status_code, response_headers)


import base64


@app.route("/history", methods=["GET"])
def history():
    before = request.args.get("before")
    after = request.args.get("after")
    limit = request.args.get("limit", default=10, type=int)
    unique = request.args.get("unique", default="false").lower() == "true"

    if before:
        before_index = int(base64.urlsafe_b64decode(before).decode("utf-8"))
        start = max(before_index - limit, 0)
    elif after:
        after_index = int(base64.urlsafe_b64decode(after).decode("utf-8"))
        start = after_index + 1
    else:
        start = 0

    end = start + limit
    paginated_history = history_manager.get_history()[start:end]

    next_cursor = (
        base64.urlsafe_b64encode(str(end).encode("utf-8")).decode("utf-8")
        if end < len(history_manager.get_history())
        else None
    )
    prev_cursor = (
        base64.urlsafe_b64encode(str(start).encode("utf-8")).decode("utf-8")
        if start > 0 and start < len(history_manager.get_history())
        else None
    )

    def unique_entries(entries):
        seen = set()
        unique_list = []
        for entry in entries:
            entry_signature = (entry.method, entry.path, entry.status_code, json.dumps(entry.headers, sort_keys=True), entry.data, json.dumps(entry.response_headers, sort_keys=True), entry.response_body)
            if entry_signature not in seen:
                seen.add(entry_signature)
                unique_list.append(entry)
        return unique_list

    if unique:
        paginated_history = unique_entries(paginated_history)

    return jsonify(
        {
            "history": [entry.to_dict() for entry in paginated_history],
            "next": next_cursor,
            "previous": prev_cursor,
            "limit": limit,
        }
    )


@app.route("/replay", methods=["POST"])
def replay():
    data = request.get_json()
    index = data.get("index")
    if index is not None and index < len(history_manager.get_history()):
        req_to_replay = history_manager.get_history()[index]
        response = requests.request(
            method=req_to_replay["method"],
            url=urljoin(app.config["UPSTREAM_URL"], req_to_replay["path"]),
            headers=req_to_replay["headers"],
            json=req_to_replay["json"],
            data=req_to_replay["data"],
        )
        return (response.content, response.status_code, response.headers.items())
    else:
        return jsonify({"error": "Invalid request index"}), 400


import click


@click.command()
@click.argument("upstream_url", required=True)
def run_server(upstream_url):
    """Start the proxy server with the given UPSTREAM_URL."""
    app.config["UPSTREAM_URL"] = upstream_url
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


if __name__ == "__main__":
    run_server()
