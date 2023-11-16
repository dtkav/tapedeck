# Test cases for cassette.py CLI commands

import pytest
import click
from click.testing import CliRunner
from cassette import cli
from unittest.mock import patch


@pytest.fixture
def runner():
    return CliRunner()


def test_history_command(runner):
    with runner.isolated_filesystem():
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "history": [
                    {
                        "method": "GET",
                        "path": "/test",
                        "status_code": 200,
                        "headers": {"Content-Type": "application/json"},
                        "data": "",
                        "response_headers": {"Content-Type": "application/json"},
                        "response_body": "response from GET /test",
                    }
                ],
                "next": None,
                "previous": None,
                "limit": 10,
            }
            result = runner.invoke(cli, ["history"])
            assert result.exit_code == 0
            expected_output = (
                "Request 1:\n"
                "GET /test HTTP/1.1\n"
                "Content-Type: application/json\n\n"
                "HTTP/1.1 200\n"
                "Content-Type: application/json\n\n"
                "response from GET /test\n\n\n"
            )
            assert expected_output in result.output


def test_replay_command_success(runner):
    with runner.isolated_filesystem():
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # Set up history
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "history": [{"method": "GET", "path": "/test"}],
                "next": None,
                "previous": None,
                "limit": 10,
            }
            # Mock replay response
            mock_post.return_value.ok = True
            result = runner.invoke(cli, ["replay"])
            assert result.exit_code == 0
            assert "Request replayed successfully\n" in result.output


def test_replay_command_failure(runner):
    with runner.isolated_filesystem():
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # Set up empty history
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "history": [],
                "next": None,
                "previous": None,
                "limit": 10,
            }
            # Mock replay response for failure
            mock_post.return_value.ok = False
            mock_post.return_value.json.return_value = {
                "error": "Invalid request index"
            }
            result = runner.invoke(cli, ["replay"])
            assert result.exit_code == 0
            assert "No requests in history to replay.\n" in result.output
