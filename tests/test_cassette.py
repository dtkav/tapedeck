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
        with patch('requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                'history': [{"method": "GET", "path": "/test"}],
                'next': None,
                'previous': None,
                'limit': 10
            }
            result = runner.invoke(cli, ['history'])
            assert result.exit_code == 0
            assert '1: GET /test\n' in result.output

def test_replay_command_success(runner):
    with runner.isolated_filesystem():
        with patch('requests.post') as mock_post:
            mock_post.return_value.ok = True
            result = runner.invoke(cli, ['replay'])
            assert result.exit_code == 0
            assert 'Request replayed successfully\n' in result.output

def test_replay_command_failure(runner):
    with runner.isolated_filesystem():
        with patch('requests.post') as mock_post:
            mock_post.return_value.ok = False
            mock_post.return_value.json.return_value = {"error": "Invalid request index"}
            result = runner.invoke(cli, ['replay'])
            assert result.exit_code == 0
            assert 'Failed to replay request: Invalid request index\n' in result.output
