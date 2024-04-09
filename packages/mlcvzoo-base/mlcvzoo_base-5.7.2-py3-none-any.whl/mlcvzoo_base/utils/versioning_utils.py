# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""
Module for defining methods that handle everything that
is related to versioning and dependencies of software.
"""
import logging
from typing import Dict, List, Tuple

import git
import pkg_resources
from git import InvalidGitRepositoryError

logger = logging.getLogger(__name__)


def get_installed_package_versions() -> Dict[str, str]:
    """
    Get installed python packages as name/version tuples.
    """
    return {d.project_name: d.version for d in pkg_resources.working_set}


def get_installed_package_list() -> List[str]:
    """
    Get installed python packages.
    """
    return ["{}=={}".format(d.project_name, d.version) for d in pkg_resources.working_set]


def get_installed_pip_package_versions() -> List[str]:
    """
    Get versions of installed pip packages.
    Deprecated: Use get_installed_package_list
    """
    logger.warning(
        "get_installed_pip_package_versions() is a deprecated alias for get_installed_package_list()"
    )
    return get_installed_package_list()


def get_git_info() -> Tuple[str, str, str]:
    """
    Get info about the current git repository

    Returns:
        Tuple consisting of
        - repository identifier
        - sha as string
        - branch-name as string
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        sha: str = str(repo.head.object.hexsha)

        try:
            branch: str = str(repo.active_branch)
        except TypeError as type_error:
            branch = str(type_error)

        return str(repo), sha, branch
    except InvalidGitRepositoryError:
        logger.warning("Could not find a valid git repository for SCM info")
        return "non-scm", "", ""


def write_pip_info_to_file(output_requirements_path: str) -> None:
    """
    Args:
        output_requirements_path: Path to the requirements file to generate
    """
    with open(file=output_requirements_path, mode="w") as pip_package_file:
        pip_packages = get_installed_pip_package_versions()
        for pip_package in pip_packages:
            pip_package_file.write(f"{pip_package}\n")
        logger.info(
            "Wrote currently installed package version to requirements file: %s",
            pip_package_file,
        )
