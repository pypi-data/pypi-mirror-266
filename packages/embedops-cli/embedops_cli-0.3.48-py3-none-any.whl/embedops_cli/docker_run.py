"""
`docker_run`
=======================================================================
Module will take a local run context and run a job locally in Docker
"""
# skip pylint too-many-branches and too-many-statements warnings
# pylint: disable=R0912, disable=R0915

import os
import re
import subprocess
import logging
import sys
from sys import platform, stdout
from shutil import which, get_terminal_size
from dotenv import dotenv_values

from embedops_cli.utilities import echo_error_and_fix
from embedops_cli.environment_utilities import PROJECT_ENV_FILE
from embedops_cli.utilities import quote_str_for_platform
from embedops_cli import environment_utilities as envutil
from embedops_cli.embedops_authorization import get_registry_token, user_secrets
from .eo_types import (
    NoDockerContainerException,
    InvalidDockerContainerException,
    NoDockerCLIException,
    DockerImageForBootstrapNotFound,
    DockerImageNotFoundException,
    DockerNotRunningException,
    LocalRunContext,
    UnknownDockerException,
    SshDirDoesNotExistException,
    SshDirIsNotADirectoryException,
)

if platform not in ("win32"):
    import termios
    import struct
    import fcntl
    import pty
else:
    import winpty  # pylint: disable=import-error

# print ascii embedops logo from docker run scripts in git bash without issue
stdout.reconfigure(encoding="utf-8")


MAX_CONTAINER_NAME_LENGTH = 30
_logger = logging.getLogger(__name__)


def _remove_special_char(string):
    """
    Remove special characters from the input string.
    """
    # Make an RE character set and pass it as an argument
    # into the compile function
    string_check = re.compile("[~`!@#$%^&*()+=}{\\[\\]|\\\\:;\"'<>?/,]")

    # Remove the special characters
    clean_string = string_check.sub("", string)

    return clean_string


def _clean_job_name(job_name):
    """
    Remove special characters, spaces from the input job name string,
    and truncate it if necessarily.
    """
    # Checkpoint 1: Check for disallowed characters and remove them.
    # Allowed characters: [a-zA-Z0-9][a-zA-Z0-9_.-]
    clean_job_name = _remove_special_char(job_name)

    # Remove spaces
    clean_job_name = clean_job_name.replace(" ", "")

    # Checkpoint 2: Check for the string length and truncate it if necessarily.
    # Container name can only be up to 30 characters long
    if len(clean_job_name) > MAX_CONTAINER_NAME_LENGTH:
        clean_job_name = clean_job_name[0:MAX_CONTAINER_NAME_LENGTH]

    return clean_job_name


def _exec_dockercmd(dockercmd, terminal=False):
    _logger.debug(subprocess.list2cmdline(dockercmd))

    _rc = None

    if terminal:
        with subprocess.Popen(dockercmd, text=True) as process:
            process.wait()
        _rc = 0
    else:
        _rc, stderr_output = (
            _pty_windows(dockercmd) if platform in ("win32") else _pty_unix(dockercmd)
        )

    if _rc != 0 and not terminal:
        if "Is the docker daemon running?" in stderr_output:
            raise DockerNotRunningException
        docker_image_errors = [
            "Requested image not found",
            "repository does not exist or may require",
            "no such host",
        ]
        if _rc == 125 and any(error in stderr_output for error in docker_image_errors):
            raise DockerImageNotFoundException
        return _rc
    envutil.delete_job_env_file()

    return _rc


# TODO: check that we have a script, docker_tag, and job_name
# TODO: add exceptions to eo_types and raise in here for different issues
def _create_docker_command(
    run_context: LocalRunContext,
    docker_cache: bool,
    secrets_file: str,
    terminal: bool = False,
):
    _handle_docker_tag(run_context)

    # We're assuming the tool is run from the same directory as the CI YAML
    _pwd = (
        os.getcwd().replace("\\", "\\\\")
        if platform in ("win32", "cygwin")
        else os.getcwd()
    )
    container_name = _clean_job_name(run_context.job_name)

    _logger.debug(f"Current working directory: {_pwd}")
    _logger.debug(f"Clean container name: {container_name}")

    script = ";".join(run_context.script)

    _logger.debug(f"Script as string: {script}")

    # add AWS credential for DinD
    aws_token_data = get_registry_token(secrets_file=secrets_file)
    aws_token_data["AWS_ACCESS_KEY_ID"] = aws_token_data.pop("registry_token_id")
    aws_token_data["AWS_SECRET_ACCESS_KEY"] = aws_token_data.pop(
        "registry_token_secret"
    )
    run_context.variables.update(aws_token_data)

    envutil.create_job_env_file(run_context.variables)

    dockercmd = ["docker", "run", "--rm", "-t"]

    if terminal:
        dockercmd.extend(["-i", "--entrypoint", ""])

    if not docker_cache:
        dockercmd.extend(["--pull=always"])

    if os.path.exists(envutil.JOB_ENV_FILE):
        dockercmd.extend([f"--env-file={envutil.JOB_ENV_FILE}"])

    _handle_ssh(dockercmd)

    quoted_script = quote_str_for_platform(script)

    # remove embedops-azure-run if found
    pattern = r"embedops-azure-run \"(.*?)\""
    results = re.search(pattern, quoted_script)
    if results:
        quoted_script = f"'{results.group(1)}'"

    if terminal:
        _docker_run_cmd_arg = ["/bin/bash", "-l"]
    else:
        _docker_run_cmd_arg = ["/bin/bash", "-l", "-i", "-c", "-e", script]

    dockercmd.extend(
        [
            "--name",
            container_name,
            "-v",
            f"{_pwd}:/eo_workdir",
            "-w",
            "/eo_workdir",
            "-e",
            f"EO_WORKDIR={_pwd}",
            "-e",
            "EO_CLI=1",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
        ]
        + (
            ["-e", f"LOCAL_UID={os.getuid()}", "-e", f"LOCAL_GID={os.getgid()}"]
            if platform in ("linux", "linux2")
            # env var set by CLI and used by EmbedOps image
            # entrypoint to handle local permissions for non-linux OS
            else [
                "-e",
                "LINUX=0",
            ]
        )
        + (
            # Put user directly into ci user if requesting a terminal
            ["-u", "ci"]
            if terminal
            else []
        )
        + [
            "-i",
            run_context.docker_tag,
            *_docker_run_cmd_arg,
        ]
    )
    return dockercmd


def docker_run(
    run_context: LocalRunContext, docker_cache: bool, terminal: bool = False
):
    """Takes a run context and launches Docker with the parameters"""
    dockercmd = _create_docker_command(
        run_context,
        docker_cache,
        secrets_file=user_secrets,
        terminal=terminal,
    )
    return _exec_dockercmd(dockercmd, terminal)


def docker_cli_run(cmd: list[str]):
    """Helper function for executing docker cli commands"""
    _logger.debug(f"Execute docker cli command: {cmd}")

    if which("docker") is None:
        # cross-platform method to see that docker cli exists.
        # running subprocess.run without a shell does not return
        #   exit code 127, but a FileNotFoundError so we check before
        echo_error_and_fix(NoDockerCLIException())

    cmd.insert(0, "docker")

    if platform == "Windows":
        cmd.insert(0, "powershell")

    try:
        output = subprocess.run(
            args=cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        _logger.debug(f"{cmd} returned {output}")

    except subprocess.CalledProcessError as err:
        _logger.debug(f"cmd {cmd} caused an exception")
        # non zero return code
        if err.returncode == 1:
            # Docker info says docker server is not running
            echo_error_and_fix(DockerNotRunningException())
        else:
            echo_error_and_fix(UnknownDockerException())

    return True


def _handle_docker_tag(run_context: LocalRunContext):
    if run_context.docker_tag is None:
        raise DockerImageForBootstrapNotFound()

    if run_context.docker_tag == "":
        raise NoDockerContainerException()

    if "http://" in run_context.docker_tag:
        raise InvalidDockerContainerException()


def _handle_ssh(dockercmd):
    embedops_ssh_dir = dotenv_values(PROJECT_ENV_FILE).get("EMBEDOPS_SSH_DIR")
    # grab ssh config and keys for any git related work
    if embedops_ssh_dir:
        # bind mount specified directory into /tmp/.ssh (which is later copied in entrypoint.sh)
        _logger.debug(f"EMBEDOPS_SSH_DIR {embedops_ssh_dir}")
        ssh_dir = os.path.expanduser(embedops_ssh_dir)
        if not os.path.exists(ssh_dir):
            raise SshDirDoesNotExistException
        if not os.path.isdir(ssh_dir):
            raise SshDirIsNotADirectoryException
        dockercmd.extend(["-v", f"{ssh_dir}:/tmp/.ssh"])
    else:
        # bind-mount host user's ~/.ssh directory
        dockercmd.extend(
            ["-v", f"{os.path.expanduser('~')}{os.path.sep}.ssh:/home/ci/.ssh"]
        )


def _pty_windows(cmd: list[str]):
    # set pty to match terminal size
    cols, rows = get_terminal_size().columns, get_terminal_size().lines
    process = winpty.PTY(cols, rows, timeout=0)

    process.spawn(subprocess.list2cmdline(cmd))

    # pywinpty does not differentiate between stdout and stderr
    # so we capture all of the output and and analyze it on error
    # to raise appropriate Exception
    output = ""
    try:
        while True:
            text = process.read()
            if text:
                output += text
                print(text, end="")
            # for currently unknown reason, EOF is not sent
            # when command within docker container completes,
            # so break if process completes
            elif not process.isalive():
                break
    except winpty.WinptyError as err:
        # ignore error raised if we read() and have reached EOF.
        # a race condition was encountered when using .iseof()
        # before using .read(), so capturing and ignoring the
        # the error to avoid it
        if str(err) != "Standard out reached EOF":
            raise err
    _rc = process.get_exitstatus()
    del process
    return _rc, output


def _pty_unix(cmd: list[str]):
    # analyzes stderr to raise appropriate exception.
    # use a pseudo ty for stderr to get nicer output.
    # `docker run` command puts docker image pull in stderr
    # so we want to make sure that animation is kept
    parent_stderr_fd, child_stderr_fd = pty.openpty()
    # allow code to proceed if no stderr to read
    os.set_blocking(parent_stderr_fd, False)
    popen_args = {"stderr": child_stderr_fd}
    stderr_output = ""  # caputer stderr for parsing error

    # set pty to match terminal size
    winsize = struct.pack(
        "HHHH", os.get_terminal_size().lines, os.get_terminal_size().columns, 0, 0
    )
    fcntl.ioctl(parent_stderr_fd, termios.TIOCSWINSZ, winsize)

    with subprocess.Popen(cmd, text=True, **popen_args) as process:
        while True:
            try:
                err_data = os.read(parent_stderr_fd, 1024)
            except BlockingIOError:
                pass
            else:
                if err_data:
                    stderr_output += err_data.decode()
                    print(err_data.decode(), end="", file=sys.stderr)
            # used to check for empty output in Python2, but seems
            # to work with just poll in 2.7.12 and 3.5.2
            # if output == '' and process.poll() is not None:
            if process.poll() is not None:
                os.close(parent_stderr_fd)
                os.close(child_stderr_fd)
                break
    _rc = process.poll()
    return _rc, stderr_output
