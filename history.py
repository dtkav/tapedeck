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
    http_version: str = "HTTP/1.1"  # Default to HTTP/1.1 if not provided

    def to_dict(self):
        """Convert the HistoryEntry instance to a dictionary."""
        return {
            'method': self.method,
            'path': self.path,
            'http_version': self.http_version,  # Include the http_version in the dictionary
            'status_code': self.status_code,
            'headers': self.headers,
            'data': self.data,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
        }

    @classmethod
    def from_dict(cls, entry_dict):
        """Create a HistoryEntry instance from a dictionary, ignoring the 'timestamp' field."""
        # Remove the 'timestamp' field if it exists in the entry_dict
        entry_dict.pop('timestamp', None)
        return cls(
            method=entry_dict['method'],
            path=entry_dict['path'],
            http_version=entry_dict.get('http_version', 'HTTP/1.1'),
            status_code=entry_dict['status_code'],
            headers=entry_dict['headers'],
            data=entry_dict['data'],
            response_headers=entry_dict['response_headers'],
            response_body=entry_dict['response_body'],
        )

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
        request_line = f"{self.method} {self.path} {self.http_version}\n"
        request_headers = ''.join(f"{k}: {v}\n" for k, v in self.headers.items())
        request_section = f"{request_line}{request_headers}\n{self.data}\n\n" if self.data else f"{request_line}{request_headers}\n"

        status_line = f"{self.http_version} {self.status_code}\n"
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
