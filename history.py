from dataclasses import dataclass
import json
import os
from datetime import datetime

@dataclass
class HistoryEntry:
    method: str
    path: str
    status_code: int
    headers: dict
    data: str
    response_headers: dict
    response_body: str

    @classmethod
    def from_request(cls, request, response):
        """Create a HistoryEntry from a requests request and response objects."""
        return cls(
            method=request.method,
            path=request.url,
            status_code=response.status_code,
            headers=dict(request.headers),
            data=request.body or "",
            response_headers=dict(response.headers),
            response_body=response.text
        )

    @classmethod
    def from_response(cls, response):
        """Create a HistoryEntry from a requests response object."""
        return cls(
            method=response.request.method,
            path=response.request.url,
            status_code=response.status_code,
            headers=dict(response.request.headers),
            data=response.request.body or "",
            response_headers=dict(response.headers),
            response_body=response.text
        )

    def format_as_http_message(self) -> str:
        request_line = f"{self.method} {self.path} HTTP/1.1\n"
        request_headers = ''.join(f"{k}: {v}\n" for k, v in self.headers.items())
        request_section = f"{request_line}{request_headers}\n{self.data}\n\n" if self.data else f"{request_line}{request_headers}\n"

        status_line = f"HTTP/1.1 {self.status_code}\n"
        response_headers = ''.join(f"{k}: {v}\n" for k, v in self.response_headers.items())
        response_section = f"{status_line}{response_headers}\n{self.response_body}\n" if self.response_body else f"{status_line}{response_headers}\n"

        return f"{request_section}{response_section}"

class HistoryManager:
    HISTORY_FILE_PATH = "request_history.json"

    def __init__(self):
        self._history = self._load_history_from_file()

    def _load_history_from_file(self):
        if os.path.exists(self.HISTORY_FILE_PATH):
            with open(self.HISTORY_FILE_PATH, 'r') as file:
                history_data = json.load(file)
                return [HistoryEntry(**entry) for entry in history_data]
        return []

    def _save_history_to_file(self):
        with open(self.HISTORY_FILE_PATH, 'w') as file:
            history_data = [entry.__dict__ for entry in self._history]
            json.dump(history_data, file, default=str)

    def append(self, entry: HistoryEntry):
        self._history.append(entry)
        self._save_history_to_file()

    def get_history(self):
        return self._history
