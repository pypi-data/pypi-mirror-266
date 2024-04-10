"""
Contains the Embedops CLI specific SSE definitions
and the actions we take upon receiving them
"""

import os
import json
import urllib.request
from urllib.error import URLError
import click

# Event types
SSE_TEXT_EVENT = "CLIEventCommandText"
SSE_RESULT_EVENT = "CLIEventCommandResult"
SSE_FILE_EVENT = "CLIEventArtifactFiles"

# Colors for log levels
LOG_LEVEL_COLOR_MAP = {"info": "white", "warning": "yellow", "error": "bright_red"}


def sse_print_command_text(event):
    """Print the text from SSE_TEXT_EVENT"""

    text_event_obj = json.loads(event.data)
    error = text_event_obj["logLevel"] == "error"
    click.secho(
        text_event_obj["displayText"],
        err=error,
        fg=LOG_LEVEL_COLOR_MAP[text_event_obj["logLevel"]],
    )


def sse_process_file_event(event, hil_results_dir: str):
    """Download all files locally from SSE_FILE_EVENT"""

    try:

        data = json.loads(event.data)

        if len(data["files"]) > 0:

            # Create parent if it does not exist
            parent_path = os.path.join(
                hil_results_dir, os.path.dirname(data["files"][0]["path"])
            )
            os.makedirs(parent_path)

            for file in data["files"]:
                dest = os.path.join(hil_results_dir, file["path"])
                urllib.request.urlretrieve(file["downloadUrl"], dest)

    except URLError as exc:
        print(f"Error downloading HIL results files: {exc}")
