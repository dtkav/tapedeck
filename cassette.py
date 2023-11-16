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
            history = response.json()['history']
            for i, entry in enumerate(history, 1):
                self.stdout.write(f"{i}: {entry['method']} {entry['path']}\n")
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
def replay():
    """Replay the last request in the history."""
    cli = ProxyCLI()
    cli.do_replay_last(None)

@cli.command()
@click.option('--repl', is_flag=True, help='Drop into the REPL command loop.')
def repl(repl):
    """Drop into the REPL command loop."""
    if repl:
        ProxyCLI().cmdloop()

if __name__ == "__main__":
    cli()

if __name__ == "__main__":
    main()
