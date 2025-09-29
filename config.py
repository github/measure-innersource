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

from constants import DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE
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
        chunk_size (int): The number of items to process at once when fetching data (for memory efficiency)
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
        chunk_size: int = 100,
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
        self.chunk_size = chunk_size

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
            f"{self.rate_limit_bypass},"
            f"{self.chunk_size}"
            ")"
        )


def get_bool_env_var(env_var_name: str, default: bool = False) -> bool:
    """Get a boolean environment variable with proper type conversion.

    This function retrieves an environment variable and converts it to a boolean.
    Only the string "true" (case-insensitive) is considered True; all other
    values are considered False.

    Args:
        env_var_name (str): The name of the environment variable to retrieve.
        default (bool, optional): The default value to return if the environment
                                 variable is not set or is empty. Defaults to False.

    Returns:
        bool: True if the environment variable is set to "true" (case-insensitive),
              False otherwise, or the default value if the variable is not set.

    Examples:
        >>> os.environ['TEST_VAR'] = 'true'
        >>> get_bool_env_var('TEST_VAR')
        True
        >>> get_bool_env_var('NONEXISTENT_VAR', default=True)
        True
    """
    ev = os.environ.get(env_var_name, "")
    if ev == "" and default:
        return default
    return ev.strip().lower() == "true"


def get_int_env_var(env_var_name: str) -> int | None:
    """Get an integer environment variable with proper type conversion and validation.

    This function retrieves an environment variable and attempts to convert it to an integer.
    If the conversion fails or the variable is not set, it returns None.

    Args:
        env_var_name (str): The name of the environment variable to retrieve.

    Returns:
        int | None: The value of the environment variable as an integer, or None if
                   the variable is not set, empty, or cannot be converted to an integer.

    Examples:
        >>> os.environ['PORT'] = '8080'
        >>> get_int_env_var('PORT')
        8080
        >>> get_int_env_var('NONEXISTENT_VAR')
        None
        >>> os.environ['INVALID_INT'] = 'not-a-number'
        >>> get_int_env_var('INVALID_INT')
        None
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
    Get and validate all environment variables required for the InnerSource measurement tool.

    This function loads environment variables from the system and an optional .env file,
    validates them, and returns a structured EnvVars object containing all configuration
    needed to run the tool.

    Args:
        test (bool, optional): If True, skip loading the .env file (used for testing).
                              Defaults to False.

    Returns:
        EnvVars: A structured object containing all validated environment variables
                and configuration settings.

    Raises:
        ValueError: If required environment variables are missing or invalid:
                   - Missing GitHub authentication (GH_TOKEN or GitHub App credentials)
                   - Missing or invalid REPOSITORY format (must be "owner/repo")
                   - Incomplete GitHub App credentials (missing ID, key, or installation ID)

    Environment Variables Required:
        Authentication (choose one):
        - GH_TOKEN: GitHub personal access token
        - GH_APP_ID + GH_APP_PRIVATE_KEY + GH_APP_INSTALLATION_ID: GitHub App credentials

        Repository:
        - REPOSITORY: Repository to analyze in "owner/repo" format

        Optional:
        - GH_ENTERPRISE_URL: GitHub Enterprise URL (for on-premises installations)
        - GITHUB_APP_ENTERPRISE_ONLY: Set to "true" for GHE-only GitHub Apps
        - REPORT_TITLE: Custom title for the report (default: "InnerSource Report")
        - OUTPUT_FILE: Output filename (default: "innersource_report.md")
        - RATE_LIMIT_BYPASS: Set to "true" to bypass rate limiting
        - CHUNK_SIZE: Number of items to process at once (default: 100, minimum: 10)

    Examples:
        >>> os.environ['GH_TOKEN'] = 'ghp_...'
        >>> os.environ['REPOSITORY'] = 'octocat/Hello-World'
        >>> env_vars = get_env_vars()
        >>> print(env_vars.owner)
        'octocat'
        >>> print(env_vars.repo)
        'Hello-World'
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

    # Get the chunk size for processing data in batches (for memory efficiency)
    chunk_size_str = os.getenv("CHUNK_SIZE", str(DEFAULT_CHUNK_SIZE))
    try:
        chunk_size = int(chunk_size_str)
        # Ensure a reasonable minimum chunk size
        chunk_size = max(chunk_size, MIN_CHUNK_SIZE)
    except ValueError:
        # Default to DEFAULT_CHUNK_SIZE if not a valid integer
        chunk_size = DEFAULT_CHUNK_SIZE

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
        chunk_size,
    )
