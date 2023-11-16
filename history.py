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

    def format_as_http_message(self) -> str:
        request_line = f"{self.method} {self.path} HTTP/1.1\n"
        request_headers = ''.join(f"{k}: {v}\n" for k, v in self.headers.items())
        request_section = f"{request_line}{request_headers}\n{self.data}\n\n" if self.data else f"{request_line}{request_headers}\n"

        status_line = f"HTTP/1.1 {self.status_code}\n"
        response_headers = ''.join(f"{k}: {v}\n" for k, v in self.response_headers.items())
        response_section = f"{status_line}{response_headers}\n{self.response_body}\n" if self.response_body else f"{status_line}{response_headers}\n"

        return f"{request_section}{response_section}"

HISTORY_FILE_PATH = "request_history.json"

def save_history_to_file(history):
    with open(HISTORY_FILE_PATH, 'w') as file:
        json.dump(history, file, default=str)

def load_history_from_file():
    if os.path.exists(HISTORY_FILE_PATH):
        with open(HISTORY_FILE_PATH, 'r') as file:
            return json.load(file)
    return []
