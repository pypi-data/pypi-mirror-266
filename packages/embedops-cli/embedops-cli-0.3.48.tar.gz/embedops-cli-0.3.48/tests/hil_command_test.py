# These tests apply to all HIL commands (ie are handled by the HIL command code in embedops_cli before calling subcommands)


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


def get_run_result():

    """Utility function to invoke the command and return the result"""

    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["run"])
    return cli_result


def test_hil_command_repo_id_not_found(mocker):

    """Test the result of the run command when the repo ID could not be found"""

    mocker.patch("embedops_cli.config.get_repo_id", return_value=None)

    cli_result = get_run_result()
    assert eo_types.NoRepoIdException.ERROR_MSG in cli_result.output
    assert eo_types.NoRepoIdException.ERROR_FIX in cli_result.output
    assert cli_result.exit_code != 0

def test_blink_command_repo_id_not_found_file_exists():

    """Test the result of the blink command when the repo_id.yml file exists but the repo_id key doesn't exist"""

    # Copy the file which contains no repo ID
    config_path = os.path.join(os.path.abspath(os.path.curdir), 'tests', 'file_fixtures', 'repo_id_not_exists.yml')
    os.mkdir('.embedops')
    shutil.copyfile(config_path, os.path.join(os.path.curdir, '.embedops', 'repo_id.yml'))

    runner = CliRunner()
    cli_result = runner.invoke(embedops_cli.hil, ["blink"])
    assert eo_types.NoRepoIdException.ERROR_MSG in cli_result.output
    assert eo_types.NoRepoIdException.ERROR_FIX in cli_result.output
    assert cli_result.exit_code != 0
