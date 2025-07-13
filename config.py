"""A module for managing environment variables used in GitHub

This module defines a class for encapsulating environment variables
and a function to retrieve these variables.

Classes:
    EnvVars: Represents the collection of environment variables used in the script.

Functions:
    get_env_vars: Retrieves and returns an instance of EnvVars populated with environment variables.
"""

import os
from os.path import dirname, join

from dotenv import load_dotenv


class EnvVars:
    # pylint: disable=too-many-instance-attributes
    """
    Environment variables

    Attributes:
        gh_app_id (int | None): The GitHub App ID to use for authentication
        gh_app_installation_id (int | None): The GitHub App Installation ID to use for
            authentication
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes to use for
            authentication
        gh_token (str | None): GitHub personal access token (PAT) for API authentication
        ghe (str): The GitHub Enterprise URL to use for authentication
        report_title (str): The title of the report
        owner (str): The owner of the repository to measure InnerSource collaboration in
        repo (str): The name of the repository to measure InnerSource collaboration in
        output_file (str): The name of the file to write the report to
        rate_limit_bypass (bool): If set to TRUE, bypass the rate limit for the GitHub API
    """

    def __init__(
        self,
        gh_app_id: int | None,
        gh_app_installation_id: int | None,
        gh_app_private_key_bytes: bytes,
        gh_app_enterprise_only: bool,
        gh_token: str | None,
        ghe: str | None,
        report_title: str,
        owner: str,
        repo: str,
        output_file: str,
        rate_limit_bypass: bool = False,
    ):
        self.gh_app_id = gh_app_id
        self.gh_app_installation_id = gh_app_installation_id
        self.gh_app_private_key_bytes = gh_app_private_key_bytes
        self.gh_app_enterprise_only = gh_app_enterprise_only
        self.gh_token = gh_token
        self.ghe = ghe
        self.report_title = report_title
        self.owner = owner
        self.repo = repo
        self.output_file = output_file
        self.rate_limit_bypass = rate_limit_bypass

    def __repr__(self):
        return (
            f"EnvVars("
            f"{self.gh_app_id},"
            f"{self.gh_app_installation_id},"
            f"{self.gh_app_private_key_bytes},"
            f"{self.gh_app_enterprise_only},"
            f"{self.gh_token},"
            f"{self.ghe},"
            f"{self.report_title},"
            f"{self.owner},"
            f"{self.repo},"
            f"{self.output_file},"
            f"{self.rate_limit_bypass}"
        )


def get_bool_env_var(env_var_name: str, default: bool = False) -> bool:
    """Get a boolean environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable as a boolean.
    """
    ev = os.environ.get(env_var_name, "")
    if ev == "" and default:
        return default
    return ev.strip().lower() == "true"


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable.

    Args:
        env_var_name: The name of the environment variable to retrieve.

    Returns:
        The value of the environment variable as an integer or None.
    """
    env_var = os.environ.get(env_var_name)
    if env_var is None or not env_var.strip():
        return None
    try:
        return int(env_var)
    except ValueError:
        return None


def get_env_vars(test: bool = False) -> EnvVars:
    """
    Get the environment variables for use in the script.

    Returns EnvVars object with all environment variables
    """
    if not test:  # pragma: no cover
        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

    gh_app_id = get_int_env_var("GH_APP_ID")
    gh_app_private_key_bytes = os.environ.get("GH_APP_PRIVATE_KEY", "").encode("utf8")
    gh_app_installation_id = get_int_env_var("GH_APP_INSTALLATION_ID")
    gh_app_enterprise_only = get_bool_env_var("GITHUB_APP_ENTERPRISE_ONLY")

    if gh_app_id and (not gh_app_private_key_bytes or not gh_app_installation_id):
        raise ValueError(
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set"
        )

    gh_token = os.getenv("GH_TOKEN")
    if (
        not gh_app_id
        and not gh_app_private_key_bytes
        and not gh_app_installation_id
        and not gh_token
    ):
        raise ValueError("GH_TOKEN environment variable not set")

    ghe = os.getenv("GH_ENTERPRISE_URL", default="").strip()

    repository = os.getenv("REPOSITORY", default="")
    if not repository:
        raise ValueError("REPOSITORY environment variable not set")
    if "/" not in repository:
        raise ValueError(
            "REPOSITORY environment variable must be in the format 'owner/repo'"
        )
    owner, repo = repository.split("/", 1)

    report_title = os.getenv("REPORT_TITLE", "InnerSource Report")
    output_file = os.getenv("OUTPUT_FILE")
    if not output_file:
        output_file = "innersource_report.md"
    rate_limit_bypass = get_bool_env_var("RATE_LIMIT_BYPASS", False)

    return EnvVars(
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        gh_app_enterprise_only,
        gh_token,
        ghe,
        report_title,
        owner,
        repo,
        output_file,
        rate_limit_bypass,
    )
