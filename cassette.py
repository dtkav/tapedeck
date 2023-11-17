from history import HistoryEntry
import requests
import click
from cmd import Cmd

from history import HistoryEntry


PROXY_SERVICE_URL = "http://localhost:5000"


# Moved _replay_request function outside of the ProxyCLI class to fix NameError
def _replay_request(index):
    """Helper method to replay a request by its index in the history."""
    response = requests.post(
        f"{PROXY_SERVICE_URL}/__/replay", json={"index": index}
    )
    proxy_origin = response.headers.get('X-Proxy-Origin')
    if proxy_origin == 'proxy':
        # If the error is from the proxy server, output the traceback and error message
        try:
            # Attempt to parse the response as JSON to get the error message and traceback
            error_info = response.json()
            error_message = error_info.get("error", "Unknown error")
            traceback_info = error_info.get("traceback", "No traceback available")
        except ValueError:
            # If JSON parsing fails, use the raw content as the error message
            error_message = response.content.decode('utf-8', errors='replace')
            traceback_info = "Traceback could not be parsed from response."
        return f"{traceback_info}\n{error_message}\n", False
    else:
        # Serialize the response using the HistoryEntry serializer
        from datetime import datetime  # Make sure this import is at the top of the file
        replayed_entry = HistoryEntry.from_response(response, timestamp=datetime.utcnow())
        formatted_entry = replayed_entry.format_as_http_message()
        return formatted_entry, True

class ProxyCLI(Cmd):
    prompt = "> "

    def do_history(self, _):
        """Fetch and display the history of proxied requests with full HTTP message exchange."""
        response = requests.get(f"{PROXY_SERVICE_URL}/__/history")
        if response.ok:
            from history import (
                HistoryEntry,
            )  # Ensure this import is at the top of the file

            history_entries = response.json()["history"]
            for i, entry_dict in enumerate(history_entries, 1):
                entry = HistoryEntry(**entry_dict)
                formatted_entry = entry.format_as_http_message()
                self.stdout.write(f"Request {i}:\n{formatted_entry}\n")
            return 0  # Ensure we return 0 to indicate success
        else:
            self.stdout.write("Failed to fetch history\n")
            return 1  # Return a non-zero value to indicate failure

    def do_replay(self, arg=None):
        """Replay a request by its index in the history, or the last request if no index is provided."""
        try:
            index = int(arg) - 1 if arg is not None else None
        except ValueError:
            self.stdout.write("Please provide a valid number or leave blank to replay the last request.\n")
            return

        formatted_entry, success = _replay_request(index if index is not None else -1)
        self.stdout.write(formatted_entry + "\n" if success else formatted_entry)

    def do_replay_last(self, _):
        """Replay the last request in the history."""
        response = requests.get(f"{PROXY_SERVICE_URL}/__/history")
        if response.ok:
            history = response.json()["history"]
            if not history:
                self.stdout.write("No requests in history to replay.\n")
                return
            last_request_index = len(history) - 1
            self.do_replay(
                str(last_request_index)
            )  # Adding 1 because the index displayed to the user is 1-based
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
@click.option('--unique', is_flag=True, help='Filter history to only include unique requests, excluding the timestamp.')
def history(unique):
    """Fetch and display the history of proxied requests with full HTTP message exchange."""
    params = {'unique': 'true'} if unique else {}
    response = requests.get(f"{PROXY_SERVICE_URL}/__/history", params=params)
    click.echo("history")
    if response.ok:
        history = response.json()["history"]
        for i, raw_entry in enumerate(history, 1):
            entry = HistoryEntry(
                method=raw_entry["method"],
                path=raw_entry["path"],
                status_code=raw_entry["status_code"],
                headers=raw_entry["headers"],
                data=raw_entry["data"],
                response_headers=raw_entry["response_headers"],
                response_body=raw_entry["response_body"],
                timestamp=raw_entry["timestamp"],
                http_version=raw_entry.get("http_version", "HTTP/1.1"),
            )
            formatted_entry = entry.format_as_http_message()
            click.echo(f"Request {i}:\n{formatted_entry}\n")
    else:
        click.echo("Failed to fetch history\n")


@cli.command()
def replay():
    """Replay the last request in the history."""
    response = requests.get(f"{PROXY_SERVICE_URL}/__/history")
    if response.ok:
        history = response.json()["history"]
        if history:
            last_request_index = len(history) - 1  # Get the index of the last request
            message, success = _replay_request(last_request_index)
            click.echo(f"{message}")
        else:
            click.echo("No requests in history to replay.")
    else:
        click.echo("Failed to fetch history")


if __name__ == "__main__":
    cli()

