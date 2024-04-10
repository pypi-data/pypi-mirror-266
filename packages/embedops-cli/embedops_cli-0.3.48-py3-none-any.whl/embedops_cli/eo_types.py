"""
`eo_types`
=======================================================================
Module will hold the enum classes for EmbedOps Tools
* Author(s): Bailey Steinfadt
"""

from enum import Enum
from os import getcwd
from termcolor import colored

EO_SUPPORT_EMAIL = "support@embedops.io"

GH_CI_CONFIG_FILENAME = ".github/workflows/embedops.yml"
BB_CI_CONFIG_FILENAME = "bitbucket-pipelines.yml"
GL_CI_CONFIG_FILENAME = ".gitlab-ci.yml"
AD_CI_CONFIG_FILENAME = "azure-pipelines.yml"
EO_CI_CONFIG_FILENAME = ".embedops-ci.yml"
SUPPORTED_CI_FILENAMES = [
    BB_CI_CONFIG_FILENAME,
    GL_CI_CONFIG_FILENAME,
    EO_CI_CONFIG_FILENAME,
    AD_CI_CONFIG_FILENAME,
    GH_CI_CONFIG_FILENAME,
]

EMBEDOPS_REGISTRY = "623731379476.dkr.ecr.us-west-2.amazonaws.com"


class YamlType(Enum):
    """Types of Yaml Files EmbedOps Tools supports"""

    UNSUPPORTED = 0
    GITLAB = 1
    BITBUCKET = 2
    GITHUB = 3


class LocalRunContext:
    """Object to store the context for locally run CI jobs"""

    def __init__(
        self,
        job_name: str,
        docker_tag: str,
        script_lines: list = None,
        variables: dict = None,
    ):
        self._job_name = job_name.strip('"')
        self._docker_tag = docker_tag.strip('"')
        if script_lines is None:
            self._script = []
        else:
            self._script = script_lines
        if variables is None:
            self._variables = {}
        else:
            self._variables = variables

    def __repr__(self) -> str:
        return f"""{self.docker_tag}/{self.job_name}"""

    def __str__(self) -> str:
        return self.pretty(use_color=False)

    def pretty(self, use_color=True) -> str:
        """provide the formatted version of the parsed job
        for the end-user

        Args:
            use_color (bool, optional): color-encode the return value. Defaults to True.

        Returns:
            str: the formatted string
        """
        name = colored(self.job_name, "magenta") if use_color else self.job_name
        details = "\n".join(
            [
                f"  Image: {self.docker_tag}",
                "  Variables:",
            ]
            + [f"    - {v}" for v in self.variables]
            + [
                "  Script:",
            ]
            + [f"    - {v}" for v in self.script]
        )
        return f"{name}\n" + colored(details, "white") if use_color else details

    @property
    def job_name(self):
        """String with the name of the job"""
        return self._job_name

    @property
    def docker_tag(self):
        """String for the Docker tag the job will be launched in"""
        return self._docker_tag

    @docker_tag.setter
    def docker_tag(self, docker_tag):
        self._docker_tag = docker_tag

    @property
    def script(self):
        """List containing the job's script from the YAML file, if it exists"""
        return self._script

    @property
    def variables(self):
        """Dictionary with any variables defined in the YAML file"""
        return self._variables


##################################################################################################
########################################### EXCEPTIONS ###########################################
##################################################################################################


class EmbedOpsException(Exception):
    """Base class for all EmbedOps exceptions"""

    def __init__(
        self, message="EmbedOps encountered an internal error", fix_message=""
    ):
        self.message = message
        self.fix_message = fix_message
        super().__init__(self.message)


############################################## YAML ##############################################


class UnsupportedYamlTypeException(EmbedOpsException):
    """Raised when an Unsupported YAML type is input"""

    ERROR_MSG = "CI configuration YAML file is not one of the supported filenames\n"
    ERROR_FIX = (
        "Make sure one of the following CI configuration files is in the current directory:\n"
        "    " + "\n    ".join(SUPPORTED_CI_FILENAMES) + "\n"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NoYamlFileException(EmbedOpsException):
    """Raised when no YAML file is found"""

    ERROR_MSG = f"CI configuration YAML file could not be found in {getcwd()}\n"
    ERROR_FIX = (
        "Make sure you are at the root of a repository that is configured w/ EmbedOps\n"
        "and that one of the following CI configuration files is in the current directory:\n"
        "    " + "\n    ".join(SUPPORTED_CI_FILENAMES) + "\n\n"
        "If the CI configuration file of interest does not match any of the above,\n"
        "specify the filename with the --filename option"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class BadTomlFileException(EmbedOpsException):
    """Raised when a bad TOML file is found"""

    ERROR_MSG = "User tokens file could not be parsed\n"
    ERROR_FIX = (
        "Delete your ~/.eosecrets.toml file and login again\n"
        f"Email {EO_SUPPORT_EMAIL} if you continue to have issues."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class BadYamlFileException(EmbedOpsException):
    """Raised when a bad YAML file is found"""

    ERROR_MSG = "CI configuration YAML file could not be parsed\n"
    ERROR_FIX = (
        "Check your YAML for syntax errors. \n"
        f"Email {EO_SUPPORT_EMAIL} if you have questions."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class MultipleYamlFilesException(EmbedOpsException):
    """Raised when multiple YAML files are found"""

    ERROR_MSG = "Multiple CI configuration files were found.\n"
    ERROR_FIX = (
        "Please specify the desired CI configuration file by using the --filename flag.\n\n"
        "Syntax: embedops-cli jobs --filename <PATH_TO_CI_CONFIG_FILE> run <JOB_NAME>"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


######################################### Authorization ##########################################


class UnauthorizedUserException(EmbedOpsException):
    """Raised when there is no Authorization Token found in the user's secrets file"""

    ERROR_MSG = "No EmbedOps credentials found\n"

    ERROR_FIX = (
        "If you have an account, maybe you've tried to do something that requires\n"
        "you to log in to your EmbedOps account. Please run `embedops-cli login`\n"
        "and then retry this command again.\n\n"
        "If you do not have an account and would like to learn more about EmbedOps,\n"
        f"contact {EO_SUPPORT_EMAIL}."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class UserDeclinedException(EmbedOpsException):
    """Raised when auth0 indicates user clicked deny"""

    ERROR_MSG = (
        "Server indicates user did not click confirm and may have clicked cancel\n"
    )

    ERROR_FIX = (
        "You may have clicked cancel on the webpage that was launched to confirm\n"
        "your account instead of confirm. Try logging in again and if you do not\n"
        "have an account and would like to learn more about EmbedOps,\n"
        f"contact {EO_SUPPORT_EMAIL}."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NoUserAssignmentException(EmbedOpsException):
    """Raised when the user has a valid account, but has not yet been assigned
    to an Organization or Group.
    """

    ERROR_MSG = "No org or group assignments\n"

    ERROR_FIX = (
        "You have a valid account, but you need an administrator to assign an\n"
        "organization and group to your account.\n"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class TokenFailureException(EmbedOpsException):
    """Raised when logging into the Embedops backend fails due to invalid token"""

    ERROR_MSG = "A problem was encountered while using your EmbedOps token.\n"

    ERROR_FIX = (
        "Your token may have expired, try running embedops-cli login to get a new token\n"
        "If you encounter further issues, please contact support:\n"
        f"{EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class LoginFailureException(EmbedOpsException):
    """Raised when logging into the Embedops backend fails"""

    ERROR_MSG = "A problem was encountered while logging into EmbedOps.\n"

    ERROR_FIX = (
        "Check your credentials on app.embedops.io and try again.\n"
        "If you encounter further issues, please contact support:\n"
        f"{EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class ExpiredTokenException(EmbedOpsException):
    """Raised when a token has expired ie gitlab"""

    ERROR_MSG = "A problem was encountered while using a login token\n"

    ERROR_FIX = (
        "Try logging in with 'embedops-cli login` and rerunning this command\n"
        "If you encounter further issues, please contact support:\n"
        f"{EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class LoginTimeoutException(EmbedOpsException):
    """Raised when a login takes longer than the timeout"""

    ERROR_MSG = "The login timeout timer elapsed while trying to login\n"

    ERROR_FIX = (
        "Try logging in with 'embedops-cli login` and rerunning this command\n"
        "If you encounter further issues, please contact support:\n"
        f"{EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class SSLException(EmbedOpsException):
    """Raised when CA certificate verification for EmbedOps fails"""

    ERROR_MSG = (
        "Valid CA Certificate not found for secure connection to app.embedops.io\n"
    )

    ERROR_FIX = (
        "Possible solutiions:\n"
        "- Use a python virtual environment\n"
        "- Contact your IT department and ensure the CA certificates listed at\n"
        "  https://www.amazontrust.com/repository are included in the CA certificates list\n\n"
        f"If the above does not help, please contact support: {EO_SUPPORT_EMAIL}\n"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


############################################# Docker #############################################


class NoDockerCLIException(EmbedOpsException):
    """Raised when docker command is not available"""

    ERROR_MSG = "docker command not found on path\n"
    ERROR_FIX = (
        "EmbedOps CLI requires a Docker installation and that it be on the path.\n"
        "Head to https://docs.docker.com/get-docker and follow the instructions to install Docker."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NoDockerContainerException(EmbedOpsException):
    """Raised when no Docker container is found in the CI configuration file"""

    ERROR_MSG = (
        "Docker container is not found in the job or in the CI configuration file.\n"
    )
    ERROR_FIX = (
        "A Docker container must be provided to run a job.\n\n"
        "For GitLab CI, use the `image` keyword.\n"
        "It can be used as part of a job, in the `default` section, or globally.\n\n"
        "For GitHub CI, use the `uses` keyword and point to the appropriate bootstrap image.\n"
        "It can only be used as part of a job."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class InvalidDockerContainerException(EmbedOpsException):
    """Raised when an invalid Docker container is detected"""

    ERROR_MSG = "Docker container is invalid.\n"
    ERROR_FIX = (
        "If your Docker container is hosted on a private registry,\n"
        "do not include http:// in your Docker container link."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerNotRunningException(EmbedOpsException):
    """Raised when the Docker daemon is not running as reported by docker info"""

    ERROR_MSG = "Docker info reports that the Docker server is not running\n"
    ERROR_FIX = (
        "Start or restart Docker desktop. \n"
        "Look for the whale logo in your system status tray\n"
        'and check that it says "Docker Desktop running"'
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerRegistryException(EmbedOpsException):
    """Raised when a problem accessing the registry is encountered"""

    ERROR_MSG = "We were unable to authenticate with the container registry\n"
    ERROR_FIX = (
        "Use error logs above, if present, to determine cause of failure.\n"
        "If using Docker Desktop for Linux, make sure password store 'pass' is initialized\n"
        "(https://docs.docker.com/desktop/get-started/#signing-in-with-docker-desktop-for-linux)\n"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerImageNotFoundException(EmbedOpsException):
    """Raised when image specified is not found"""

    ERROR_MSG = "Incorrect image name\n"
    ERROR_FIX = (
        "Check and make sure the the image specified\n"
        "for the job in the CI YAML is correct\n"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class DockerImageForBootstrapNotFound(EmbedOpsException):
    """Raised when an image is not specfied for a job that uses a bootstrap image"""

    ERROR_MSG = (
        "EMBEDOPS_IMAGE variable not specified for job that uses a bootstrap image\n"
    )
    ERROR_FIX = "Set EMBEDOPS_IMAGE: <image>:<version> in the job's YAML section\n"

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class UnknownDockerException(EmbedOpsException):
    """Raised when an error with Docker is encountered that we haven't otherwise handled"""

    ERROR_MSG = "It appears that Docker is unavailable or\nsome other error with Docker has occurred. \n"  # pylint: disable=C0301
    ERROR_FIX = (
        "1) Verify Docker is running on your machine and try again.\n"
        "2) If Docker was already running, restart Docker and try again.\n"
        "3) If you encounter further issues, please contact support:\n"
        f"{EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class SshDirDoesNotExistException(EmbedOpsException):
    """Raised when the directory specified in EMBEDOPS_SSH_DIR does not exist"""

    ERROR_MSG = "EMBEDOPS_SSH_DIR directory does not exist.\n"
    ERROR_FIX = "Set the correct path for EMBEDOPS_SSH_DIR in your host environment."

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class SshDirIsNotADirectoryException(EmbedOpsException):
    """Raised when the path specified in EMBEDOPS_SSH_DIR is not a directory"""

    ERROR_MSG = "EMBEDOPS_SSH_DIR path is not a directory.\n"
    ERROR_FIX = "Set the correct path for EMBEDOPS_SSH_DIR in your host environment."

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


######################################### General Errors #########################################


class NoRepoIdException(EmbedOpsException):
    """Raised when the repo id could not be found"""

    ERROR_MSG = f"Project's repo id not found in {getcwd()}\n"
    ERROR_FIX = (
        "This command requires a valid repo ID file (.embedops/repo_id.yml)\n"
        "in the current working directory. Make sure you are the root of a\n"
        "repository that is configured w/ EmbedOps."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NoCIRunIdException(EmbedOpsException):
    """Raised when the ci run id not provided"""

    ERROR_MSG = "ci run id not found\n"
    ERROR_FIX = (
        "CI Pipeline HIL runs require a valid CIRun ID provided.\n"
        "Verify your EMBEDOPS_HOST and other platform communication\n"
        "settings are correct in your CI provider settings."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)


class NetworkException(EmbedOpsException):
    """Raised when a general network error occurs"""

    ERROR_MSG = "network exception: "
    ERROR_FIX = (
        "Please check your network connection.\n"
        f"For assistance, contact your account administrator or email {EO_SUPPORT_EMAIL}"
    )

    def __init__(
        self,
        status_code: int,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(f"{message}: status code: {status_code}", fix_message)
        self.status_code = status_code


class NoAvailableHilDevice(EmbedOpsException):
    """Raised when a no available HIL device is detected for CI HIL Run"""

    ERROR_MSG = "HIL Gateway device error\n"
    ERROR_FIX = (
        "There are no HIL Gateway devices currently provisioned to your account."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        # fix_message passed in from platform
        super().__init__(message, fix_message)


class HILGatewayDeviceLimitExceededException(EmbedOpsException):
    """Raised when a HIL fleet has not yet been created for the given account"""

    ERROR_MSG = "HIL Gateway device limit exceeded\n"
    ERROR_FIX = (
        "Contact an account administrator or email support@embedops.io in order\n"
        "to provision more HIL Gateways."
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        # fix_message passed in from platform
        super().__init__(message, fix_message)
        super().__init__("HIL gateway device error", fix_message)


class UnknownShellException(EmbedOpsException):
    """Raised when a subprocess exits unexpectedly or with an unhandled error"""

    ERROR_FIX = (
        "Check that the command is valid and the executable is on the path"
        f"Email {EO_SUPPORT_EMAIL} if there are further issues"
    )

    def __init__(
        self,
        cmd,
        fix_message=ERROR_FIX,
    ):
        message = f"Shell command '{cmd}' returned unhandled error"
        super().__init__(message, fix_message)


class UnknownException(EmbedOpsException):
    """Raised when embedops-cli raises an unhandled exception"""

    ERROR_MSG = "Unhandled exception raised:\n"
    ERROR_FIX = (
        "Try your command again and consider enabling debug output"
        f"Email {EO_SUPPORT_EMAIL} if there are further issues"
    )

    def __init__(
        self,
        message=ERROR_MSG,
        fix_message=ERROR_FIX,
    ):
        super().__init__(message, fix_message)
