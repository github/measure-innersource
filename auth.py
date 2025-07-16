"""GitHub authentication module for the InnerSource measurement tool.

This module provides functions for authenticating with GitHub using either Personal Access
Tokens (PAT) or GitHub App installations. It supports both GitHub.com and GitHub Enterprise
Server installations.

Authentication Methods:
    1. Personal Access Token (PAT) - Simple token-based authentication
    2. GitHub App Installation - More secure app-based authentication with JWT

The module handles the complexity of different authentication methods and provides
a unified interface for establishing authenticated connections to GitHub's API.

Functions:
    auth_to_github: Create an authenticated GitHub client connection
    get_github_app_installation_token: Obtain installation tokens for GitHub Apps

Dependencies:
    - github3.py: GitHub API client library
    - requests: HTTP library for API calls
"""

import github3
import requests


def auth_to_github(
    token: str,
    gh_app_id: int | None,
    gh_app_installation_id: int | None,
    gh_app_private_key_bytes: bytes,
    ghe: str,
    gh_app_enterprise_only: bool,
) -> github3.GitHub:
    """
    Establish an authenticated connection to GitHub.com or GitHub Enterprise.

    This function creates an authenticated GitHub client using either Personal Access Token
    or GitHub App authentication. It supports both GitHub.com and GitHub Enterprise
    installations.

    Authentication Priority:
    1. GitHub App authentication (if all app credentials are provided)
    2. Personal Access Token authentication (if token is provided)

    Args:
        token (str): The GitHub personal access token for authentication.
                    Can be empty if using GitHub App authentication.
        gh_app_id (int | None): The GitHub App ID for app-based authentication.
                               Required along with other app credentials for app auth.
        gh_app_installation_id (int | None): The GitHub App Installation ID.
                                            Required for app-based authentication.
        gh_app_private_key_bytes (bytes): The GitHub App Private Key as bytes.
                                         Required for app-based authentication.
        ghe (str): The GitHub Enterprise URL (e.g., "https://github.company.com").
                  Leave empty for GitHub.com.
        gh_app_enterprise_only (bool): Set to True if the GitHub App is created
                                      on GitHub Enterprise and should only communicate
                                      with the GHE API endpoint.

    Returns:
        github3.GitHub: An authenticated GitHub client object that can be used
                       to make API calls to GitHub.

    Raises:
        ValueError: If authentication fails due to:
                   - Missing required credentials (no token or incomplete app credentials)
                   - Unable to establish connection to GitHub

    Examples:
        >>> # Using Personal Access Token
        >>> client = auth_to_github(token="ghp_...", gh_app_id=None,
        ...                        gh_app_installation_id=None,
        ...                        gh_app_private_key_bytes=b"",
        ...                        ghe="", gh_app_enterprise_only=False)

        >>> # Using GitHub App
        >>> client = auth_to_github(token="", gh_app_id=12345,
        ...                        gh_app_installation_id=67890,
        ...                        gh_app_private_key_bytes=private_key_bytes,
        ...                        ghe="", gh_app_enterprise_only=False)
    """
    if gh_app_id and gh_app_private_key_bytes and gh_app_installation_id:
        if ghe and gh_app_enterprise_only:
            gh = github3.github.GitHubEnterprise(url=ghe)
        else:
            gh = github3.github.GitHub()
        gh.login_as_app_installation(
            gh_app_private_key_bytes, gh_app_id, gh_app_installation_id
        )
        github_connection = gh
    elif ghe and token:
        github_connection = github3.github.GitHubEnterprise(url=ghe, token=token)
    elif token:
        github_connection = github3.login(token=token)
    else:
        raise ValueError(
            "GH_TOKEN or the set of [GH_APP_ID, GH_APP_INSTALLATION_ID, \
                GH_APP_PRIVATE_KEY] environment variables are not set"
        )

    if not github_connection:
        raise ValueError("Unable to authenticate to GitHub")
    return github_connection  # type: ignore


def get_github_app_installation_token(
    ghe: str,
    gh_app_id: str,
    gh_app_private_key_bytes: bytes,
    gh_app_installation_id: str,
) -> str | None:
    """
    Obtain a GitHub App Installation access token using JWT authentication.

    This function creates a JWT token using the GitHub App's private key and exchanges
    it for an installation access token that can be used to authenticate API requests
    on behalf of the installed app.

    Reference: https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation

    Args:
        ghe (str): The GitHub Enterprise endpoint URL (e.g., "https://github.company.com").
                  Leave empty for GitHub.com.
        gh_app_id (str): The GitHub App ID as a string.
        gh_app_private_key_bytes (bytes): The GitHub App Private Key in bytes format.
                                         This should be the complete private key including
                                         the header and footer.
        gh_app_installation_id (str): The GitHub App Installation ID as a string.
                                     This identifies the specific installation of the app.

    Returns:
        str | None: The installation access token if successful, None if the request
                   fails or if there's an error in the authentication process.

    Raises:
        No exceptions are raised directly, but request failures are handled gracefully
        and logged to the console.

    Notes:
        - The token has a default expiration time (typically 1 hour)
        - The token provides access to resources the app installation has been granted
        - Network errors and API failures are handled gracefully with None return

    Examples:
        >>> private_key = b"-----BEGIN PRIVATE KEY-----\\n[key content]\\n-----END PRIVATE KEY-----"
        >>> token = get_github_app_installation_token(
        ...     ghe="",
        ...     gh_app_id="12345",
        ...     gh_app_private_key_bytes=private_key,
        ...     gh_app_installation_id="67890"
        ... )
        >>> if token:
        ...     print("Successfully obtained installation token")
    """
    jwt_headers = github3.apps.create_jwt_headers(gh_app_private_key_bytes, gh_app_id)
    api_endpoint = f"{ghe}/api/v3" if ghe else "https://api.github.com"
    url = f"{api_endpoint}/app/installations/{gh_app_installation_id}/access_tokens"

    try:
        response = requests.post(url, headers=jwt_headers, json=None, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    return response.json().get("token")
