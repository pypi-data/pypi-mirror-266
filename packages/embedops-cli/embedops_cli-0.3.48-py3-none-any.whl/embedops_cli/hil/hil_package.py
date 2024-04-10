"""
The hil_package library includes functions for creating and extracting HIL execution packages.
These packages are ZIP-based and contain the build artifacts, HIL tests, and metadata for a
given HIL run.
"""
import os
import tempfile
import shutil
import json
from embedops_cli.utilities import logging_setup, requests

_logger = logging_setup(__name__)

# The fixed name of the HIL manifest file within the execution package
HIL_MANIFEST_NAME = "hil_manifest.json"

# The fixed name of the user's hil root folder within the execution package
HIL_ROOT_FOLDER_NAME = "hil"

# The fixed name of the external modules path within the execution package
HIL_EXTERNAL_MODULES_FOLDER_NAME = "external_modules"

# Passed to the shutil.make_archive tool
HIL_ARCHIVE_FORMAT = "zip"

# Regex that matches the HIL results folder names
HIL_RESULTS_FOLDER_NAME_PATTERN = (
    "hil_results_[0-9][0-9][0-9][0-9]_[0-9][0-9]_[0-9][0-9]"
    "_[0-9][0-9]H_[0-9][0-9]M_[0-9][0-9]S"
)


def create_hil_package(
    build_artifacts: list[str],
    hil_directory: str,
    external_modules_path: str,
    manifest_data: dict,
    out_path: str,
) -> bool:
    """

    Build a HIL execution package archive. The inputs are copied to a temporary directory
    prior to zipping.

    :param build_artifacts: A list of paths to files that are considered build artifacts
    :param hil_directory: Path to the repository's hil root directory
    :param external_modules_path: Path to external modules directory, or None if none exists
    :param manifest_data: Dictionary of data that will be inserted into the package's
    manifest JSON file (eg, Git data)
    :param out_path: Full output path of the package, including the file name
    :return: True if success; False otherwise
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        _logger.debug(f"creating execution package from artifacts: {build_artifacts}")
        # Copy all artifacts into temporary dir
        artifacts_path = os.path.join(tmp_dir, "artifacts")
        os.mkdir(artifacts_path)
        for artifact in build_artifacts:
            artifact_name = os.path.basename(artifact)

            if os.path.isfile(artifact):
                shutil.copyfile(artifact, os.path.join(artifacts_path, artifact_name))
            else:
                return False

        shutil.copytree(
            hil_directory,
            os.path.join(tmp_dir, HIL_ROOT_FOLDER_NAME),
            ignore=shutil.ignore_patterns(HIL_RESULTS_FOLDER_NAME_PATTERN),
        )

        # If external modules exist, copy
        if external_modules_path is not None:
            shutil.copytree(
                external_modules_path,
                os.path.join(tmp_dir, HIL_EXTERNAL_MODULES_FOLDER_NAME),
            )

        # Write the manifest file
        with open(
            os.path.join(tmp_dir, HIL_MANIFEST_NAME), "w", encoding="utf-8"
        ) as m_file:
            json.dump(manifest_data, m_file, indent=4)

        # Create the actual archive file
        out_archive_path = os.path.splitext(out_path)[0]
        shutil.make_archive(out_archive_path, HIL_ARCHIVE_FORMAT, tmp_dir)

    # Only return success if the outfile exists
    if os.path.isfile(out_path):
        return True

    return False


def upload_hil_package(package_path: str, url: str) -> bool:
    """
    Upload a HIL package ZIP to the given S3 bucket pre-signed URL. This function assumes
    that the file exists.
    """
    _logger.debug(f"Starting upload of HIL package")

    headers = {
        "Content-Type": "application/zip",
        "x-amz-server-side-encryption": "AES256",
    }

    with open(package_path, "rb") as archive_file:
        data = archive_file.read()
        response = requests.put(
            url,
            headers=headers,
            data=data,
            timeout=60,
        )

        _logger.debug(f"HIL package upload response: {str(response)}\n")

    return response.status_code
