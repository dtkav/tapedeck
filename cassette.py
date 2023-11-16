import requests
import click
from cmd import Cmd

PROXY_SERVICE_URL = "http://localhost:5000"


class ProxyCLI(Cmd):
    prompt = "> "

    def do_history(self, _):
        """Fetch and display the history of proxied requests."""
        response = requests.get(f"{PROXY_SERVICE_URL}/history")
        if response.ok:
            history = response.json()
            for i, entry in enumerate(history, 1):
                self.stdout.write(f"{i}: {entry['method']} {entry['path']}\n")
        else:
            self.stdout.write("Failed to fetch history\n")

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
            if history:
                last_request_index = len(history) - 1
                self.do_replay(str(last_request_index + 1))  # Adding 1 because the index displayed to the user is 1-based
            else:
                self.stdout.write("No requests in history to replay.\n")
        else:
            self.stdout.write("Failed to fetch history\n")

    def do_exit(self, _):
        """Exit the CLI."""
        return True


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ProxyCLI command line interface.')
    parser.add_argument('--repl', action='store_true', help='Drop into the REPL command loop.')
    args = parser.parse_args()

    if args.repl:
        ProxyCLI().cmdloop()
    else:
        cli = ProxyCLI()
        cli.do_replay_last(None)
