# Test cases for cassette.py CLI commands

import pytest
from unittest.mock import patch, MagicMock
from cassette import ProxyCLI

@pytest.fixture
def mock_cli():
    cli = ProxyCLI()
    cli.stdout = MagicMock()
    return cli

def test_history_command(mock_cli):
    with patch('requests.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = [
            {"method": "GET", "path": "/test"}
        ]
        mock_cli.onecmd('history')
        mock_cli.stdout.write.assert_called_with('1: GET /test\n')

def test_replay_command_success(mock_cli):
    with patch('requests.post') as mock_post:
        mock_post.return_value.ok = True
        mock_cli.onecmd('replay 1')
        mock_cli.stdout.write.assert_called_with('Request replayed successfully\n')

def test_replay_command_failure(mock_cli):
    with patch('requests.post') as mock_post:
        mock_post.return_value.ok = False
        mock_post.return_value.json.return_value = {"error": "Invalid request index"}
        mock_cli.onecmd('replay 99')
        mock_cli.stdout.write.assert_called_with('Failed to replay request: Invalid request index\n')

def test_exit_command(mock_cli):
    assert mock_cli.onecmd('exit') == True
