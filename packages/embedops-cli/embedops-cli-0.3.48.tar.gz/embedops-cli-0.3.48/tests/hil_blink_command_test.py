import os
import json
import pytest
import shutil
from urllib3 import PoolManager
from click.testing import CliRunner
from embedops_cli import embedops_cli
from tests.utilities import mock_sse
from embedops_cli import eo_types

mock_exit_event_rc0 = [{"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 0})}]
mock_exit_event_rc9 = [{"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 9})}]


@pytest.fixture(autouse=True)
def configure_env(monkeypatch, mocker):

    shutil.rmtree('.embedops', ignore_errors=True)  # Remove any previous embedops folder

    # Patch stuff for request mocking
    monkeypatch.setattr(PoolManager, "request", mock_sse.mock_sse_request_handler)

    yield

    shutil.rmtree('.embedops', ignore_errors=True)


@pytest.fixture(scope="function")
def hil_repo_id_exists():
    config_path = os.path.join(os.path.abspath(os.path.curdir), 'tests', 'file_fixtures', 'repo_id_exists.yml')
    os.mkdir('.embedops')
    shutil.copyfile(config_path, os.path.join(os.path.curdir, '.embedops', 'repo_id.yml'))

    yield

    shutil.rmtree('.embedops')


def test_blink_command_unauthorized(mocker, hil_repo_id_exists):

    """Test a successful invocation of the hil blink command"""

    # Stub a few functions to avoid making an actual call
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_BAD)

    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.embedops_cli, ["hil", "blink"])

    assert cli_result.exit_code == 1


def test_blink_command_success(mocker, hil_repo_id_exists):

    """Test a successful invocation of the hil blink command"""

    # Stub a few functions to avoid making an actual call
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_GOOD)

    mock_sse.set_mock_events(mock_exit_event_rc0)

    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["blink"])

    assert cli_result.exit_code == 0


def test_blink_command_exit_code(mocker, hil_repo_id_exists):

    """Test that the exit code event received from the server affects the exit code of the CLI"""

    # Stub a few functions to avoid making an actual call
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_GOOD)

    mock_sse.set_mock_events(mock_exit_event_rc9)

    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["blink"])

    assert cli_result.exit_code == 9


def test_blink_command_prints(mocker, hil_repo_id_exists):

    """Test that the text commands from the server actually print to stdout and stderr"""

    # Stub a few functions to avoid making an actual call
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_GOOD)

    info_str = "some stdout info text"
    warn_str = "some stdout warning text"
    error_str = "some stderr error text"

    #TODO: various collections of json/mocks should be stored in dedicated functions/fixtures so that we can reuse them
    mock_events = [
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "info", "displayText": info_str})},
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "warning", "displayText": warn_str})},
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "error", "displayText": error_str})},
        {"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 0})}
    ]

    mock_sse.set_mock_events(mock_events)

    runner = CliRunner(mix_stderr=False)
    cli_result = runner.invoke(embedops_cli.hil, ["blink"])

    print(cli_result.stdout)

    assert info_str in cli_result.stdout
    assert warn_str in cli_result.stdout
    assert error_str in cli_result.stderr
    assert cli_result.exit_code == 0
