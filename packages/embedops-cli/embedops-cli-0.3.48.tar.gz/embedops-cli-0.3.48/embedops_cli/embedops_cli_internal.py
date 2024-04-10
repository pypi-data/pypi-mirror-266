"""
`embedops_cli_internal`
=======================================================================
Helper functions to remove implementation from top level cli command handling
"""

import sys
import logging
import click
from urllib3.exceptions import MaxRetryError
from embedops_cli.api.rest import ApiException
from embedops_cli.utilities import echo_error_and_fix

# import embedops_cli.yaml_tools.yaml_utilities as yaml_utilities
from embedops_cli.yaml_tools import yaml_utilities
from embedops_cli.docker_run import docker_cli_run
from embedops_cli.hil.hil_types import (
    HILRepoId404Exception,
)
from . import version, embedops_authorization
from .eo_types import (
    BadYamlFileException,
    DockerNotRunningException,
    LoginFailureException,
    UnsupportedYamlTypeException,
    UnauthorizedUserException,
    DockerRegistryException,
    UnknownDockerException,
    NetworkException,
    NoUserAssignmentException,
    SSLException,
)


_logger = logging.getLogger(__name__)


def _embedops_cli_help(ctx: click.Context):
    click.secho("-" * 80, fg="magenta")
    click.secho(
        "\n╭━━━╮╱╱╭╮╱╱╱╱╱╱╭┳━━━╮\n"
        "┃╭━━╯╱╱┃┃╱╱╱╱╱╱┃┃╭━╮┃\n"
        "┃╰━━┳╮╭┫╰━┳━━┳━╯┃┃╱┃┣━━┳━━╮\n"
        "┃╭━━┫╰╯┃╭╮┃┃━┫╭╮┃┃╱┃┃╭╮┃━━┫\n"
        "┃╰━━┫┃┃┃╰╯┃┃━┫╰╯┃╰━╯┃╰╯┣━━┃\n"
        "╰━━━┻┻┻┻━━┻━━┻━━┻━━━┫╭━┻━━╯\n"
        "╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱┃┃\n"
        "╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰╯\n",
        fg="magenta",
    )
    click.secho(
        "\nWelcome to EmbedOps CLI",
        err=False,
        fg="magenta",
    )
    click.secho("Version: " + version.__version__ + "\n")
    click.secho(
        "EmbedOps provides web-based and command-line tools that make setting\n"
        "up and maintaining your builds smooth and simple.\n\n"
        "EmbedOps tools also integrate directly with your automated CI\n"
        "pipelines, allowing any developer to run steps in their local dev\n"
        "environment exactly as it would be run on the CI server.\n"
    )
    click.secho(
        "Examples:\n"
        '"embedops-cli jobs show" provides a listing of the jobs that EmbedOps can run\n'
        '"embedops-cli jobs" enters an interactive mode for browsing your pipeline CI jobs\n'
        '"embedops-cli hil" enters an interactive mode for local HIL operations\n'
    )
    click.secho(
        "For a listing of all options, use embedops-cli --help, or embedops-cli -h\n"
    )
    click.secho("-" * 80, fg="magenta")
    click.secho("\n")

    ctx.exit(0)


def _say_token_is_good(token_name: str):
    click.secho(f"{token_name} Token is ", nl=False)
    click.secho("GOOD", err=False, fg="bright_green")


def _say(msg: str, new_line=True):
    click.secho(f"{msg}", err=False, nl=new_line)


def _say_available_ci_jobs(job_list: list, wrong_job_name: str = None) -> None:
    user_jobs = [j for j in job_list if j not in ["release"]]
    if wrong_job_name:
        click.secho(
            f'\nJob "{wrong_job_name}" is not available in this CI configuration.\n',
            err=False,
            fg="yellow",
        )
    click.secho(
        f"EmbedOps CLI Jobs Available:",
        err=False,
        fg="magenta",
    )
    for j in user_jobs:
        click.secho(
            f" - {j}",
            err=False,
            fg="white",
        )


def _get_and_check_embedops_token(test: bool):
    token = embedops_authorization.get_auth_token()
    _logger.debug("Checking for valid EmbedOps token...")
    try:
        if token and embedops_authorization.check_token():
            _logger.debug("Embedops token good")
        elif test:
            click.secho("\nToken not found", err=False, fg="bright_red")
            click.secho(
                "\nuse `embedops-cli login` to log in and retrieve a token",
                err=False,
                fg="bright_red",
            )
            sys.exit(1)
        else:
            _logger.debug("No token found, request a token")
            return None
    except MaxRetryError as exc:
        if type(exc.reason).__name__ == "SSLError":
            echo_error_and_fix(SSLException())  # exits
        raise exc

    return token


def _get_and_check_registery_token():
    """Check the current token, if it fails try fetching a new token and trying again"""
    _logger.debug("Checking for valid Docker token...")
    try:
        if embedops_authorization.is_registery_token_valid():
            if not embedops_authorization.check_registry_login():
                embedops_authorization.login_to_registry()
            # We have a valid token already
        else:
            embedops_authorization.fetch_registry_token()
            embedops_authorization.login_to_registry()
    except MaxRetryError as exc:
        if type(exc.reason).__name__ == "SSLError":
            echo_error_and_fix(SSLException())  # exits
        raise exc
    except (
        UnauthorizedUserException,
        LoginFailureException,
        DockerRegistryException,
        UnknownDockerException,
        DockerNotRunningException,
        NoUserAssignmentException,
    ) as exc:
        _logger.debug("Failed to get registry token")
        echo_error_and_fix(exc)
    except (ApiException,) as exc:
        _handle_network_exception(exc)

    _logger.debug("Docker token good")
    return True


def _get_job_name_list(_filename: str) -> list:
    try:
        parser = yaml_utilities.get_correct_parser_type(_filename)
    except UnsupportedYamlTypeException as exc:
        raise UnsupportedYamlTypeException() from exc

    try:
        return parser.get_job_name_list(_filename)
    except BadYamlFileException as exc:
        raise BadYamlFileException() from exc


def _docker_is_installed_and_running():
    """Check if docker is installed and running.
    Otherwise raise exception"""

    _logger.debug(f"Check if docker is available and running...")

    return docker_cli_run(["info"])


def _handle_network_exception(exc):
    _logger.debug(f"Network exception occurred {exc}")
    if exc.status == 401:
        echo_error_and_fix(LoginFailureException())
    elif exc.status == 404:
        echo_error_and_fix(HILRepoId404Exception())
    elif isinstance(exc, ApiException):
        echo_error_and_fix(NetworkException(exc.status))
    else:
        echo_error_and_fix(exc)
