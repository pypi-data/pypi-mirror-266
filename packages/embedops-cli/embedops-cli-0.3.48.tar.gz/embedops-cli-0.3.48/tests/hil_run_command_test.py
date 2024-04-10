import os
import json
import sys
import pytest
import shutil
import embedops_cli.eo_types as eo_types
from urllib3 import PoolManager
from click.testing import CliRunner
from tests.utilities import mock_sse
from tests.utilities.fake_repo import (
    FakeRepo,
    TEST_HIL_ARTIFACTS_PATH,
)
from embedops_cli import embedops_cli
from embedops_cli.hil.hil_common import (
    get_hil_artifacts_path_from_ci_artifacts_dir,
)
from embedops_cli.hil.hil_types import (
    NoHILRootPathException,
    HILPackageCreationException,
    NoHILArtifactsPathException,
    HILFilesInvalidException,
    HILExternalModulesPathInvalidException,
    NoHILResultsPathException
)
from embedops_cli.utilities import requests

mock_exit_event_rc0 = [{"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 0})}]
mock_exit_event_rc9 = [{"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 9})}]

TEST_REPO_ID = '5040a275-ff9e-449d-8b91-76a0d4eb4451'

ResponseObject = lambda **kwargs: type("Object", (), kwargs)


# mock functions for returning the upload status
def mock_upload_response_200(url, headers=None, data=None, timeout=0):
    return ResponseObject(status_code=200)


def mock_upload_response_401(url, headers=None, data=None, timeout=0):
    return ResponseObject(status_code=403)


# Allows us to fake out the call to get_presigned_url
class MockUserClient:

    def __init__(self, upload_status):
        self.upload_status = upload_status

    def get_pre_signed_url_for_upload(self, repo_id):
        return ResponseObject(url='https://www.test.com', status=self.upload_status)


@pytest.fixture(autouse=True)
def fake_repo_instance():

    """Sets up the fake repo and CLI global objects, used by the rest of the tests"""

    fake_repo_instance = FakeRepo(TEST_REPO_ID)
    current_dir = os.getcwd()
    os.chdir(fake_repo_instance.get_fake_repo_path())

    yield fake_repo_instance

    fake_repo_instance.cleanup()
    os.chdir(current_dir)


@pytest.fixture(autouse=True)
def configure_env(monkeypatch, mocker):

    """Run before every test function to set up common mocks and stubs"""

    # Patch stuff for request mocking, all to "good" returns
    # For the run command there's three network requests: getting the URL, uploading, and the SSE run command
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_GOOD)
    monkeypatch.setattr(PoolManager, "request", mock_sse.mock_sse_request_handler)
    monkeypatch.setattr(requests, "put", mock_upload_response_200)
    mocker.patch("embedops_cli.embedops_authorization.get_user_client", return_value=MockUserClient(200))
    mocker.patch("embedops_cli.config.get_repo_id", return_value='test_repo_id')

    mock_sse.set_mock_events(mock_exit_event_rc0)

    yield


def get_run_result(mix_stderr=True):

    """Utility function to invoke the command and return the result"""

    runner = CliRunner(mix_stderr=mix_stderr)
    cli_result = runner.invoke(embedops_cli.hil, ["run"])
    return cli_result


def test_run_command_hil_root_path_not_found(fake_repo_instance):

    """Test the result of the run command when the hil/config.yml file doesn't exist"""

    fake_repo_instance.remove_hil_config_yml()

    print('executing from %s' % os.getcwd())

    cli_result = get_run_result()
    assert NoHILRootPathException.ERROR_FIX in cli_result.output
    assert NoHILRootPathException.ERROR_MSG in cli_result.output
    assert cli_result.exit_code != 0


def test_run_command_hil_root_path_not_found_file_exists(fake_repo_instance):

    """Test the result of the run command when the hil/config.yml file exists but the hil_root_path key doesn't exist"""

    fake_repo_instance.remove_hil_root_path_attr()

    cli_result = get_run_result()
    assert NoHILRootPathException.ERROR_FIX in cli_result.output
    assert NoHILRootPathException.ERROR_MSG in cli_result.output
    assert cli_result.exit_code != 0


def test_run_command_hil_artifacts_path_not_found_file_exists(fake_repo_instance):

    """Test the result of the run command when the hil/config.yml file exists but the hil_artifacts key doesn't exist"""

    fake_repo_instance.remove_hil_artifacts_path_attr()

    cli_result = get_run_result()
    assert NoHILArtifactsPathException.ERROR_FIX in cli_result.output
    assert NoHILArtifactsPathException.ERROR_MSG in cli_result.output
    assert cli_result.exit_code != 0


# def test_run_command_presigned_url_network_error(mocker):
#
#     """Test the result of the run command when the presigned URL endpoint returns != 200"""
#
#     # Re-patch to be a bad return
#     mocker.patch("embedops_cli.embedops_authorization.get_user_client", return_value=MockUserClient(404))
#
#     cli_result = get_run_result()
#     assert "network exception: 404" in cli_result.stdout
#     assert cli_result.exit_code == 1


def test_run_command_upload_network_error(monkeypatch):

    """Test the result of the run command when the upload request returns != 200"""

    # Re-patch to be a bad return
    monkeypatch.setattr(requests, "put", mock_upload_response_401)

    cli_result = get_run_result(mix_stderr=True)
    assert eo_types.NetworkException.ERROR_FIX in cli_result.output
    assert eo_types.NetworkException.ERROR_MSG in cli_result.output
    assert cli_result.exit_code != 0


def test_run_command_run_bad_auth_token(mocker):

    """Test an unauthorized (auth token is bad) call to the run command"""

    # Pretend server said our token was bad
    mocker.patch("embedops_cli.embedops_authorization.get_auth_token", return_value=mock_sse.AUTH_TOKEN_BAD)

    # Run `hil run`
    cli_result = get_run_result()

    # We should catch a NetworkException
    assert eo_types.NetworkException.ERROR_FIX in cli_result.output
    assert eo_types.NetworkException.ERROR_MSG in cli_result.output
    assert cli_result.exit_code != 0


def test_run_command_run_success():

    """Test a call to the run command"""

    cli_result = get_run_result()
    assert cli_result.exit_code == 0


def test_run_command_exit_code():

    """Test that the exit code event received from the server affects the exit code of the CLI"""
    mock_sse.set_mock_events(mock_exit_event_rc9)

    cli_result = get_run_result()
    assert cli_result.exit_code == 9


def test_run_command_prints():

    """Test that the text commands from the server actually print to stdout and stderr"""

    info_str = "some stdout info text"
    warn_str = "some stdout warning text"
    error_str = "some stderr error text"

    mock_events = [
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "info", "displayText": info_str})},
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "warning", "displayText": warn_str})},
        {"event": "CLIEventCommandText", "data": json.dumps({"logLevel": "error", "displayText": error_str})},
        {"event": "CLIEventCommandResult", "data": json.dumps({"exitCode": 0})}
    ]

    mock_sse.set_mock_events(mock_events)

    cli_result = get_run_result(mix_stderr=False)

    assert info_str in cli_result.stdout
    assert warn_str in cli_result.stdout
    assert error_str in cli_result.stderr
    assert cli_result.exit_code == 0


def test_get_hil_artifacts_path_from_ci_artifacts_dir_file_does_not_exist(
    fake_repo_instance,
):
    """Test that the returned artifact path is None if the artifacts directory does not exist"""

    fake_repo_instance.remove_artifacts_dir()

    hil_artifacts = get_hil_artifacts_path_from_ci_artifacts_dir(
        TEST_HIL_ARTIFACTS_PATH
    )
    assert hil_artifacts is None


def test_get_hil_artifacts_path_from_ci_artifacts_dir_file_exists(
    fake_repo_instance,
):
    """Test that the returned artifact path if found in the artifacts directory"""

    hil_artifacts_path = 'artifacts/test.hex'

    hil_artifacts = get_hil_artifacts_path_from_ci_artifacts_dir(
        hil_artifacts_path
    )
    assert hil_artifacts == hil_artifacts_path


def test_hil_external_modules_path_invalid_does_not_exist(fake_repo_instance):

    """Test that when defined, the external modules path must exist"""

    fake_repo_instance.add_external_modules_path("external_modules")

    # Run `hil run`
    cli_result = get_run_result()

    # We should catch a NetworkException
    assert HILExternalModulesPathInvalidException.ERROR_MSG in cli_result.output


def test_hil_run_invalid_verbosity(fake_repo_instance):

    """Test that an invalid verbosity value throws the appropriate error"""

    # Run `hil run` with arguments
    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["run", "--verbosity", "invalid"])

    # "Invalid value" is emitted by Click library
    assert "Invalid value" in cli_result.output


def test_hil_run_valid_verbosity(fake_repo_instance):

    """Test that a valid verbosity value works correctly"""

    # Run `hil run` with arguments
    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["run", "--verbosity", "debug"])

    # "Invalid value" is emitted by Click library
    assert cli_result.exit_code == 0


def test_hil_run_invalid_results_base(fake_repo_instance):

    """Test that an invalid results base throws the appropriate error"""

    fake_repo_instance.add_hil_results_base("thisfolderdoesnotexist")

    # Run `hil run` with arguments
    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["run"])

    # NoHILResultsPathException.ERROR_MSG is emitted by Click library
    assert NoHILResultsPathException.ERROR_MSG in cli_result.output


