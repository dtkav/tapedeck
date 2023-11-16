from history import HistoryEntry
import requests
import click
from cmd import Cmd

    def format_as_http_message(self) -> str:
        request_line = f"{self.method} {self.path} HTTP/1.1\n"
        request_headers = ''.join(f"{k}: {v}\n" for k, v in self.headers.items())
        request_section = f"{request_line}{request_headers}\n{self.data}\n\n" if self.data else f"{request_line}{request_headers}\n"

        status_line = f"HTTP/1.1 {self.status_code}\n"
        response_headers = ''.join(f"{k}: {v}\n" for k, v in self.response_headers.items())
        response_section = f"{status_line}{response_headers}\n{self.response_body}\n" if self.response_body else f"{status_line}{response_headers}\n"

        return f"{request_section}{response_section}"

PROXY_SERVICE_URL = "http://localhost:5000"


class ProxyCLI(Cmd):
    prompt = "> "

    def do_history(self, _):
        """Fetch and display the history of proxied requests with full HTTP message exchange."""
        response = requests.get(f"{PROXY_SERVICE_URL}/history")
        if response.ok:
            from history import HistoryEntry  # Ensure this import is at the top of the file

            history_entries = response.json()['history']
            for i, entry_dict in enumerate(history_entries, 1):
                entry = HistoryEntry(**entry_dict)
                formatted_entry = entry.format_as_http_message()
                self.stdout.write(f"Request {i}:\n{formatted_entry}\n")
            return 0  # Ensure we return 0 to indicate success
        else:
            self.stdout.write("Failed to fetch history\n")
            return 1  # Return a non-zero value to indicate failure

    def do_replay(self, arg):
        """Replay a request by its index in the history."""
        try:
            index = int(arg) - 1
            response = requests.post(
                f"{PROXY_SERVICE_URL}/replay", json={"index": index}
            )
            if response.ok:
                self.stdout.write("Request replayed successfully\n")
            else:
                error_message = response.json().get("error", "Unknown error")
                self.stdout.write(f"Failed to replay request: {error_message}\n")
        except ValueError:
            self.stdout.write("Please provide a valid number.\n")

    def do_replay_last(self, _):
        """Replay the last request in the history."""
        response = requests.get(f"{PROXY_SERVICE_URL}/history")
        if response.ok:
            history = response.json()['history']
            if not history:
                self.stdout.write("No requests in history to replay.\n")
                return
            last_request_index = len(history) - 1
            self.do_replay(str(last_request_index + 1))  # Adding 1 because the index displayed to the user is 1-based
        else:
            self.stdout.write("Failed to fetch history\n")

    def do_exit(self, _):
        """Exit the CLI."""
        return True


import click

@click.group()
def cli():
    pass

@cli.command()
def history():
    """Fetch and display the history of proxied requests with full HTTP message exchange."""
    response = requests.get(f"{PROXY_SERVICE_URL}/history")
    click.echo("history")
    if response.ok:
        history = response.json()['history']
        for i, raw_entry in enumerate(history, 1):
            entry = HistoryEntry(
                method=raw_entry['method'],
                path=raw_entry['path'],
                status_code=raw_entry['status_code'],
                headers=raw_entry['headers'],
                data=raw_entry['data'],
                response_headers=raw_entry['response_headers'],
                response_body=raw_entry['response_body']
            )
            formatted_entry = entry.format_as_http_message()
            click.echo(f"Request {i}:\n{formatted_entry}\n")
    else:
        click.echo("Failed to fetch history\n")

@cli.command()
def replay():
    """Replay the last request in the history."""
    cli = ProxyCLI()
    cli.do_replay_last(None)


if __name__ == "__main__":
    cli()
