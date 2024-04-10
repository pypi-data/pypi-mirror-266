"""
`embedops_cli`
=======================================================================
CLI interface for EmbedOps tools
"""
# skip pylint subprocess-run-check because we *are* checking the exit status
# pylint: disable=W1510
import sys
import logging
import traceback
import subprocess
import os
from datetime import datetime
import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from embedops_cli.config import get_repo_id
from embedops_cli.utilities import echo_error_and_fix
from embedops_cli import config
from embedops_cli.embedops_cli_internal import (
    _embedops_cli_help,
    _get_and_check_embedops_token,
    _get_and_check_registery_token,
    _docker_is_installed_and_running,
    _say_available_ci_jobs,
    _get_job_name_list,
    _say_token_is_good,
    _handle_network_exception,
)
from embedops_cli.api.rest import ApiException
from embedops_cli.hil.hil_commands import get_repo_fleet_devices
from embedops_cli.embedops_cli_plugins import ToolsGroupCommand

# import embedops_cli.yaml_tools.yaml_utilities as yaml_utilities
from embedops_cli.yaml_tools import yaml_utilities
from embedops_cli.hil import hil_commands
from embedops_cli.docker_run import docker_run
from . import version, embedops_authorization, telemetry
from .eo_types import (
    TokenFailureException,
    BadYamlFileException,
    EmbedOpsException,
    LoginFailureException,
    NoYamlFileException,
    UnknownException,
    UnsupportedYamlTypeException,
    MultipleYamlFilesException,
    NoDockerContainerException,
    InvalidDockerContainerException,
    UnauthorizedUserException,
    NoRepoIdException,
)

_logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help", "--halp"]}

# Commands that skip token validation
SKIP_TOKEN_COMMANDS = ["logout", "tools"]


# User specified context for subcommands
class Config:
    """Class to be used as ctx.object passed to functions by click"""

    def __init__(self, token):
        self.token = token


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(version=version.__version__)
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.option("--test", "-t", help="Test your login status", is_flag=True)
@click.pass_context
def embedops_cli(ctx: click.Context, debug, test):
    """EmbedOps Base Command"""

    # Valid python version check occurs in __init__.py

    # Enable debug output
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _logger.debug("Debug logging enabled")
    else:
        logging.basicConfig(level=logging.INFO)

    # No subcommand print help info
    if ctx.invoked_subcommand is None:
        _embedops_cli_help(ctx)

    if ctx.invoked_subcommand in SKIP_TOKEN_COMMANDS:
        # On logout, don't do any token checking or processing
        return

    # if command needs embedops token check it
    # TODO: only get embedops token if needed for subcommand
    token = _get_and_check_embedops_token(test)

    # Store token in click context for use by subcommands
    ctx.obj = Config(token)

    # if token isn't valid and we aren't currently attempting to login let user
    # know they need to login first
    # TODO: login automatically?
    if token is None and ctx.invoked_subcommand != "login":
        echo_error_and_fix(TokenFailureException())

    # If we're logging in again despite a valid token don't run these steps
    if ctx.invoked_subcommand != "login":
        # TODO: only check registry token if needed for subcommand
        # Check registry token
        registry = _get_and_check_registery_token()
        _logger.debug(f"Registry token is valid: {registry}")

        # TODO: only check docker is running if needed for subcommand
        # Check that docker is available and running
        docker = _docker_is_installed_and_running()
        _logger.debug(f"Docker is running: {docker}")

    # Continue with subcommand, handled by click...


@embedops_cli.command()
@click.pass_context
def login(ctx: click.Context):
    """Log in to the EmbedOps platform.
    You will be prompted to enter your EmbedOps credentials if you are not logged in."""

    local_config: Config = ctx.obj

    if local_config.token is None:
        _logger.debug("Requesting new embedops token")
        try:  # request a token if we don't already have one
            access_token = embedops_authorization.request_authorization()
            if access_token is None:
                raise LoginFailureException()
            embedops_authorization.set_auth_token(access_token)

        except (LoginFailureException, UnauthorizedUserException) as exc:
            echo_error_and_fix(exc)

    _say_token_is_good("EmbedOps")

    docker = _docker_is_installed_and_running()
    _logger.debug(f"Docker is running: {docker}")

    _get_and_check_registery_token()

    _say_token_is_good("Docker")

    click.secho("You are logged into EmbedOps!\n", err=False, fg="white")

    telemetry.login_event()


@embedops_cli.command()
def logout():

    """
    Perform logout operation. This deletes user secrets and logs out from Docker.
    """

    telemetry.logout_event()
    embedops_authorization.delete_secrets_file()
    embedops_authorization.docker_cli_logout()

    click.secho("You are logged out from EmbedOps!\n", err=False, fg="white")


def print_command_info(ctx: click.Context, opts: click.STRING):
    """Helper function that echoes formatted CLI equivalent commands
    when user uses the wizard functionality."""
    click.secho(f"Equivalent command:\n", fg="magenta")
    click.secho(f"\t{ctx.command_path} {opts}\n", fg="white", color="white")


@embedops_cli.group(invoke_without_command=True)
@click.option(
    "--filename",
    help="path to the CI YAML or YML file",
    required=False,
    expose_value=True,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.pass_context
def jobs(ctx: click.Context, filename):
    """Run or view CI jobs defined in
    YAML or YML files locally.

    Try the interactive jobs runner available
    by running `embedops-cli jobs`."""

    if filename is None:
        try:
            filename = yaml_utilities.get_yaml_in_directory()
        except (NoYamlFileException, MultipleYamlFilesException) as exc:
            echo_error_and_fix(exc)
    else:
        if not (filename.lower().endswith(".yaml") or filename.endswith(".yml")):
            click.secho("-" * 80, fg="bright_red")
            click.secho("File must be a .yaml or .yml file.", err=True, fg="bright_red")
            click.secho(ctx.get_usage(), err=True, fg="white")
            click.secho("-" * 80, fg="bright_red")
            sys.exit(1)
    ctx.obj = filename

    _logger.debug(f"jobs show called with file {filename}")
    if not ctx.invoked_subcommand:
        click.secho("--- user controls " + "-" * 62, fg="magenta")
        click.secho("\t   navigation    : arrow keys (← → ↑ ↓)", fg="white")
        click.secho("\t   select        : enter key  (↵)", fg="white")
        click.secho("")

        # parse yaml file to create job list
        job_name_list = _get_job_name_list(filename)

        # filter out the hil and release jobs
        # TODO: there is a separate TODO in this file around cleaning this up
        job_name_filtered_list = [
            Choice(i) for i in job_name_list if not i in ("release", "hil", "hil-start")
        ]
        # add cancel choice
        job_name_filtered_list.append(Choice(value="cancel", name="Cancel"))

        job = inquirer.select(
            message="Select which job you would like to run",
            choices=job_name_filtered_list,
            border=True,
        ).execute()

        if "cancel" == job:
            sys.exit(0)

        action = inquirer.select(
            message=f"What would you like to do for job {job}?",
            choices=[
                Choice(value="run", name="Run Locally"),
                Choice(value="describe", name="Describe Job"),
                Choice(value="cancel", name="Cancel"),
            ],
            border=True,
        ).execute()

        if "cancel" == action:
            sys.exit(0)
        if "describe" == action:
            ctx.invoke(describe, job_name=job)
        elif "run" == action:
            ctx.invoke(run, job_name=job)

        # print corresponding command
        print_command_info(ctx, f"--filename={filename} {action} {job}")


@jobs.command()
@click.pass_context
@click.argument("job_name")
@click.option(
    "--terminal",
    help="Instead of executing the job launch a terminal within the same docker build environment",
    default=False,
    required=False,
    is_flag=True,
)
@click.option(
    "--docker-cache/--no-docker-cache",
    help="Optionally disable the use of a local docker cache for EmbedOps Images",
    default=False,
    required=False,
    is_flag=True,
)
def run(ctx: click.Context, job_name, docker_cache=False, terminal=False):
    """Run a job defined in a CI YAML file.
    JOB_NAME is the name of the job or step in your CI YAML file"""

    telemetry.command_event("jobs_run", {"job_name": job_name})

    # check if token has expired if so try to get a new token
    if embedops_authorization.is_registery_token_valid() is False:
        embedops_authorization.login_to_registry()

    filename = ctx.obj
    _logger.debug(f"jobs run called with file '{filename}' and job '{job_name}")

    try:
        job = yaml_utilities.get_job(filename, job_name)
    except (
        UnsupportedYamlTypeException,
        BadYamlFileException,
    ) as exc:
        echo_error_and_fix(exc)

    # match the given job name against the job collection
    if job:
        git_hash_run = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
        )
        if git_hash_run.returncode != 0:
            git_hash = "Not Available"
        else:
            git_hash = git_hash_run.stdout.strip()
        repo_id = get_repo_id() or "N/A"
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        click.secho("-" * 80, fg="magenta")
        click.secho(f"Running job   '{job_name}'", err=False, fg="magenta")
        click.secho(f"-> cli version   '{version.__version__}'", err=False, fg="white")
        click.secho(f"-> repo id       '{repo_id}'", err=False, fg="white")
        click.secho(f"-> file          '{filename}'", err=False, fg="white")
        click.secho(f"-> directory     '{os.getcwd()}'", err=False, fg="white")
        click.secho(
            f"-> image         '{job.docker_tag if job.docker_tag else 'N/A'}'",
            err=False,
            fg="white",
        )
        click.secho(f"-> git sha       '{git_hash}'", err=False, fg="white")
        click.secho(f"-> timestamp     '{current_time}'", err=False, fg="white")
        click.secho("-" * 80, fg="magenta")
        click.secho("\n")
        try:
            run_exitcode = docker_run(job, docker_cache, terminal)
        except (
            EmbedOpsException,
            NoDockerContainerException,
            InvalidDockerContainerException,
        ) as exc:
            echo_error_and_fix(exc)
        if run_exitcode == 0:
            click.secho("\nJob ran successfully\n", err=False, fg="magenta")
        else:
            click.secho("\nJob ran with errors\n", err=True, fg="red")
    # They tried to run a job that doesn't exist, show them the jobs they can run.
    else:
        try:
            _say_available_ci_jobs(_get_job_name_list(filename), job_name)
        except (UnsupportedYamlTypeException, BadYamlFileException) as exc:
            echo_error_and_fix(exc)


@jobs.command()
@click.option(
    "-v",
    "--verbose",
    help="Show details for the available jobs in YAML file",
    required=False,
    expose_value=True,
    is_flag=True,  # Inform Click that this is a boolean flag
)
@click.pass_context
def show(ctx: click.Context, verbose):
    """Show available jobs in YAML file"""

    telemetry.command_event("jobs_show", {"verbose": verbose})

    filename = ctx.obj
    _logger.debug(f"jobs show called with file {filename}")

    if not verbose:
        try:
            job_list = _get_job_name_list(filename)
            # TODO: it would be cleaner to pass parameters into _get_job_name_list
            #       that will ignore job names
            # ignore_jobs = ["hil", "release"]
            # job_list = _get_job_name_list(filename, ignore_jobs)
            job_name_list = "\n".join(
                [i for i in job_list if not i in ("release", "hil", "hil-start")]
            )
        except (UnsupportedYamlTypeException, BadYamlFileException) as exc:
            echo_error_and_fix(exc)

        click.secho(f"\nEmbedOps CLI Jobs Available:", err=False, fg="magenta")
        click.secho(f"{job_name_list}\n", err=False, fg="white")
    else:
        try:
            job_list = yaml_utilities.get_job_list(filename)
        except (
            UnsupportedYamlTypeException,
            BadYamlFileException,
        ) as exc:
            echo_error_and_fix(exc)

        click.secho("\nEmbedOps CLI Jobs Details:\n", err=False, fg="magenta")

        # match the given job name against the job collection
        for job in job_list:
            click.secho(job.pretty())


@jobs.command()
@click.pass_context
@click.argument("job_name")
def describe(ctx: click.Context, job_name):
    """Shows details for a single job"""

    telemetry.command_event("jobs_describe", {"job_name": job_name})

    filename = ctx.obj
    _logger.debug(f"jobs describe called with file {filename}")

    try:
        job = yaml_utilities.get_job(filename, job_name)
    except (
        UnsupportedYamlTypeException,
        BadYamlFileException,
    ) as exc:
        echo_error_and_fix(exc)

    # match the given job name against the job collection
    if job is not None:
        click.secho(job.pretty())
    # They tried to show details of a job that doesn't exist, show them the jobs they can run.
    else:
        try:
            _say_available_ci_jobs(_get_job_name_list(filename), job_name)
        except (UnsupportedYamlTypeException, BadYamlFileException) as exc:
            echo_error_and_fix(exc)


@embedops_cli.group(invoke_without_command=True)
@click.option(
    "--devices",
    help='Comma delimited list of device names to run hil "blink" and "run" command on',
    required=False,
    expose_value=True,
    callback=lambda ctx, value: value.split(",") if value else None,
)
@click.pass_context
def hil(ctx: click.Context, devices):
    # pylint: disable=too-many-branches
    """Group for all hil commands.



    Try the interactive HIL runner available
    by running `embedops-cli hil`."""

    # TODO: check if repo_id.yaml exists
    repo_id = config.get_repo_id()

    if not repo_id:
        echo_error_and_fix(NoRepoIdException())

    ctx.ensure_object(dict)
    ctx.obj["devices"] = devices

    if not ctx.invoked_subcommand:

        click.secho("--- user controls " + "-" * 62, fg="magenta")
        click.secho("\t   navigation    : arrow keys (← → ↑ ↓)", fg="white")
        click.secho("\t   select        : enter key  (↵)", fg="white")
        click.secho("")
        choices = [
            Choice(value="run", name="Run Locally"),
            Choice(value="blink", name="Blink Gateway"),
            Choice(value="fleet", name="List Devices in Fleet"),
            Choice(value="provision", name="Provision New Gateway"),
            Choice(value="cancel", name="Cancel"),
        ]

        action = inquirer.select(
            message="What HIL operation would you like to do?",
            choices=choices,
            border=True,
        ).execute()

        if "cancel" == action:
            sys.exit(0)

        if "provision" == action:
            print_command_info(ctx, f"{action}")
            # invoke provision command
            ctx.invoke(getattr(hil_commands, action))
        elif "fleet" == action:
            print_command_info(ctx, f"{action}")
            # invoke fleet command
            ctx.invoke(getattr(hil_commands, action))
        else:
            try:
                repo_fleet_devices = get_repo_fleet_devices()
            except ApiException as exc:
                _handle_network_exception(exc)
                sys.exit(0)
            if len(repo_fleet_devices) >= 1:
                choices = [
                    Choice(
                        d.device_name,
                        name=f"{d.device_name} ({'Online' if d.is_online else 'Offline'})",
                    )
                    for d in repo_fleet_devices
                ]
                choices.append(Choice(value=False, name="Cancel"))
                if "run" == action:
                    choices.insert(0, Choice("any", name="Any"))
                elif "blink" == action:
                    pass
                device = inquirer.select(
                    message=f"Select a HIL Gateway to {action}",
                    choices=choices,
                    border=True,
                ).execute()

                if not device:
                    ctx.exit(0)

                if device == "any":
                    ctx.obj["devices"] = None
                    print_command_info(ctx, f"{action}")
                else:
                    ctx.obj["devices"] = [device]
                    print_command_info(ctx, f"--devices {device} {action}")

                # invoke run/blink command
                ctx.invoke(getattr(hil_commands, action))
            else:
                click.secho("no devices provided or none in fleet")


# Add sub-commands to the hil group
hil.add_command(hil_commands.blink)
hil.add_command(hil_commands.run)
hil.add_command(hil_commands.fleet)
hil.add_command(hil_commands.provision)


@embedops_cli.group(cls=ToolsGroupCommand)
def tools():
    """Top-level group for tools command (supports plugins)"""


if __name__ == "__main__":
    # Top level catch block in case there are known exception that make it to this level
    try:
        embedops_cli(prog_name="embedops-cli")  # pylint:disable=unexpected-keyword-arg
    except EmbedOpsException as err:
        # An embedops exception was not caught, catch it here to print our exception info
        echo_error_and_fix(err)
    except SystemExit as err:
        # We are calling system exit, just let this through, either we completed
        # successfully or our exception handlers called sys.exit(1)
        pass
    except Exception as err:  # pylint: disable=broad-except
        # TODO: add a telemetry event here to detect unhandled exceptions seen in the wild
        # TODO: Allow customers to disable telemetry, some don't like that being automatic
        # with no opt-out
        _logger.debug("An unexpected exception occurred")
        traceback.print_exc()
        echo_error_and_fix(UnknownException())
