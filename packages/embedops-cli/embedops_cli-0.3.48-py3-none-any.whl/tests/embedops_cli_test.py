"""
`embedops_cli_test`
=======================================================================
Unit tests for the CLI interface for EmbedOps tools
* Author(s): Bailey Steinfadt
"""

import os
import subprocess
import pytest
import shutil
from click.testing import CliRunner
from urllib3.exceptions import MaxRetryError, SSLError
from embedops_cli import embedops_cli
from embedops_cli import eo_types
from tests import BBYML_FILENAME, GLYML_FILENAME
from embedops_cli.config import settings

NOT_A_FILENAME = "not_a_file.yaml"
GHYML_TEST_DETECTION_FILENAME = "gh-pipelines/.github/workflows/test-detection-.github-ci.yml"


@pytest.fixture(autouse=True)
def configure_env(monkeypatch, mocker):
    monkeypatch.setenv("EMBEDOPS_HOST", "https://dev-01.embedops.io")
    settings.host = "https://dev-01.embedops.io:443"


@pytest.fixture(scope="session")
def change_test_dir(request):
    """
    A function-level fixture that changes to the test case directory,
    run the test (yield), then change back to the calling directory to
    avoid side-effects.
    """
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


def test_version_command():
    """Learned how to write tests for click by testing build in version command"""
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, ["--version"])
    assert result.exit_code == 0
    assert result.output[:21] == "embedops-cli, version"


def test_help_command():
    """Learned how to write tests for click by testing built in help command"""
    runner = CliRunner()
    h_result = runner.invoke(embedops_cli.embedops_cli, "-h")
    assert h_result.exit_code == 0
    help_result = runner.invoke(embedops_cli.embedops_cli, "--help")
    assert help_result.exit_code == 0
    assert help_result.output == h_result.output
    halp_result = runner.invoke(embedops_cli.embedops_cli, "--halp")
    assert halp_result.exit_code == 0
    assert halp_result.output == h_result.output


def test_jobs_command():
    """Test the top level jobs group"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs, ["--filename", "not_a_file.yaml"]
    )
    # Click returns '2' and is what checks that the filename exists
    assert result.exit_code != 0


def test_show_jobs_no_filename():
    """Test the show job list command no filename"""
    runner = CliRunner()
    result = runner.invoke(embedops_cli.jobs, ["show"])
    assert result.exit_code == 0


def test_show_jobs_nonexistent_filename():
    """Test the show job list command with a nonexistent file"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs, ["--filename", "not_a_file.yaml", "show"]
    )
    assert result.exit_code != 0


def test_show_jobs_not_yaml_filename():
    """Test the show job list command with a non-yaml filename"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs, [ "--filename", "tests/README.md", "show"]
    )
    assert result.exit_code == 1


def test_show_jobs():
    """Test the show job list command correct syntax"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", BBYML_FILENAME, "show"],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", GLYML_FILENAME, "show"],
    )
    assert result.exit_code == 0


def test_run_jobs_no_job_name_or_filename():
    """Test the run job command with no job or filename"""

    runner = CliRunner()
    result = runner.invoke(embedops_cli.jobs, [ "run"])
    assert result.exit_code == 2


def test_run_jobs_no_job_name():
    """Test the run job list command with no job name"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", BBYML_FILENAME, "run"],
    )
    assert result.exit_code == 2

# TODO: All these tests are essentially the same and could be collapsed into one
# parameterized test with a list of tuples for command and error code expected
def test_run_jobs_nonexistent_file():
    """Test the run job command with a nonexistent file"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", NOT_A_FILENAME, "run", "build"],
    )
    assert result.exit_code == 2


def test_run_jobs_not_yaml_filename():
    """Test the run job command with a non-yaml filename"""
    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", "tests/README.md", "run", "build"],
    )
    assert result.exit_code == 1


def test_stale_token_prompts_login(mocker):
    """Test that a no-longer-valid auth token prompts"""
    docker_status = mocker.patch(
        "embedops_cli.embedops_cli_internal._docker_is_installed_and_running"
    )
    docker_status.return_value = True

    token_status = mocker.patch(
        "embedops_cli.embedops_cli.embedops_authorization.check_token"
    )
    token_status.return_value = False

    do_login = mocker.patch(
        "embedops_cli.embedops_cli.embedops_authorization.request_authorization"
    )
    do_login.side_effect = eo_types.UnauthorizedUserException()
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login")
    do_login.assert_called()

    assert result.exit_code != 0

    # mock `check user` to return false
    # verify that "do login" is called
    # verify that if "do login" is successful that the return value is 0

def subprocess_err_code(errcode: int, *args, **kwargs):
    exc = subprocess.CalledProcessError(returncode=errcode, cmd=kwargs.get('args'))
    raise exc

# pretend to have a valid token
# mock _get_and_check_embedops_token
@pytest.fixture()
def fake_login_token(mocker):
    mocker.patch("embedops_cli.embedops_cli._get_and_check_embedops_token", return_value="FakeToken")

def test_docker_not_found(monkeypatch, fake_login_token):
    """Test docker command not found"""

    # simulate docker CLI not found by setting PATH to an empty string
    monkeypatch.setenv("PATH", "")

    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login")

    exception = eo_types.NoDockerCLIException

    assert result.exit_code == 1
    assert exception.ERROR_MSG in result.output
    assert exception.ERROR_FIX in result.output

@pytest.mark.parametrize("err_code, exception", [(1,eo_types.DockerNotRunningException),(2, eo_types.UnknownDockerException)])
def test_docker_not_running(mocker, err_code, exception, fake_login_token):
    """Test docker command not running"""

    # skip docker cli validation
    mocker.patch("embedops_cli.docker_run.which")

    docker_status = mocker.patch("embedops_cli.docker_run.subprocess.run")
    docker_status.side_effect = lambda *args,**kwargs:subprocess_err_code(err_code,*args,**kwargs)

    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login")

    assert result.exit_code != 0
    assert exception.ERROR_MSG in result.output
    assert exception.ERROR_FIX in result.output

@pytest.mark.parametrize("exception", [(eo_types.SSLException)])
def test_ssl_error_output_on_embedops_token_check(mocker, exception):
    """Test correct output for ssl error when grabbing Auth0 token"""
    token = "FakeToken"
    
    mocker.patch("embedops_cli.embedops_cli.embedops_authorization.get_auth_token", return_value=token)
    mocker.patch("embedops_cli.embedops_cli.embedops_authorization.check_token", side_effect=MaxRetryError(None, None, SSLError()))

    obj = embedops_cli.Config(token)
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login", obj=obj)

    assert result.exit_code == 1
    assert exception.ERROR_MSG in result.output
    assert exception.ERROR_FIX in result.output

@pytest.mark.parametrize("exception", [(eo_types.SSLException)])
def test_ssl_error_output_on_registry_token_fetch(mocker, exception):
    """Test correct output for ssl error when grabbing registry token"""
    token = "FakeToken"
    mocker.patch("embedops_cli.embedops_cli.embedops_authorization.get_auth_token", return_value=token)
    mocker.patch("embedops_cli.embedops_cli._get_and_check_embedops_token", return_value=token)
    mocker.patch("embedops_cli.embedops_cli._docker_is_installed_and_running")
    mocker.patch("embedops_cli.embedops_cli.embedops_authorization.is_registery_token_valid", return_value=False)
    mocker.patch("embedops_cli.embedops_cli.embedops_authorization.fetch_registry_token", side_effect=MaxRetryError(None, None, SSLError()))

    obj = embedops_cli.Config(token)
    runner = CliRunner()
    result = runner.invoke(embedops_cli.embedops_cli, "login", obj=obj)

    assert result.exit_code == 1
    assert exception.ERROR_MSG in result.output
    assert exception.ERROR_FIX in result.output


# turn off for CI as docker cannot be run there
# def test_gh_run_happy():
#     """run the happy path, actually runs cppcheck but just exits 0"""
#     test_file_path = 'tests/.github/workflows/embedops.yml'
#     shutil.copyfile('tests/.github/workflows/happy.yml', test_file_path)

#     runner = CliRunner()
#     result = runner.invoke(
#         embedops_cli.embedops_cli,
#         ["jobs", "--filename", test_file_path, "run", "Cppcheck"],
#     )
#     print(f'result: {result.stdout}')
#     os.remove(test_file_path)
#     assert result.exit_code == 0


def test_gh_run_jobs_no_env_embedops_image():
    """validate bad exit when no env vars defined in build step"""
    test_file_path = 'tests/gh-pipelines/.github/workflows/embedops.yml'
    shutil.copyfile('tests/gh-pipelines/.github/workflows/no_env_embedops_image.yml', test_file_path)

    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", test_file_path, "run", "Cppcheck"],
    )
    print(f'result: {result.stdout}')
    os.remove(test_file_path)
    assert result.exit_code == 1


def test_gh_run_jobs_no_with_args():
    """validate bad exit when no with.args defined in build step"""
    test_file_path = 'tests/gh-pipelines/.github/workflows/embedops.yml'
    shutil.copyfile('tests/gh-pipelines/.github/workflows/no_with_args.yml', test_file_path)

    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", test_file_path, "run", "Cppcheck"],
    )
    os.remove(test_file_path)
    assert result.exit_code != 0


def test_gh_run_jobs_no_uses_stanza():
    """validate bad exit when no uses clause in build step"""
    test_file_path = 'tests/gh-pipelines/.github/workflows/embedops.yml'
    shutil.copyfile('tests/gh-pipelines/.github/workflows/no_uses.yml', test_file_path)

    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", test_file_path, "run", "Cppcheck"],
    )
    os.remove(test_file_path)
    assert result.exit_code == 1


def test_gh_run_jobs_uses_no_docker():
    """validate bad exit when the bootstrap uses clause isn't prefixed correctly"""
    test_file_path = 'tests/gh-pipelines/.github/workflows/embedops.yml'
    shutil.copyfile('tests/gh-pipelines/.github/workflows/uses_no_docker.yml', test_file_path)

    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", test_file_path, "run", "Cppcheck"],
    )
    print(f'result: {result.stdout}')
    os.remove(test_file_path)
    assert result.exit_code == 1


def test_gh_run_jobs_no_job_name():
    """validate bad exit when using legacy style pipeline yaml for GH"""
    test_file_path = 'tests/gh-pipelines/.github/workflows/embedops.yml'
    shutil.copyfile('tests/'+GHYML_TEST_DETECTION_FILENAME, test_file_path)

    runner = CliRunner()
    result = runner.invoke(
        embedops_cli.jobs,
        ["--filename", test_file_path, "run"],
    )
    os.remove(test_file_path)
    assert result.exit_code == 2
