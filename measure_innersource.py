"""A tool for measuring InnerSource collaboration in a given repository

This script uses the GitHub API to search for issues/prs/discussions in a repository
and measure the InnerSource collaboration occuring in those issues/prs/discussions.
The results are then written to a markdown file.

"""

import shutil
from pathlib import Path

from auth import auth_to_github, get_github_app_installation_token
from config import get_env_vars
from markdown_helpers import markdown_too_large_for_issue_body, split_markdown_file


def evaluate_markdown_file_size(output_file: str) -> None:
    """
    Evaluate the size of the markdown file and split it, if it is too large.
    """
    output_file_name = output_file if output_file else "innersource_report.md"
    file_name_without_extension = Path(output_file_name).stem
    max_char_count = 65535
    if markdown_too_large_for_issue_body(output_file_name, max_char_count):
        split_markdown_file(output_file_name, max_char_count)
        shutil.move(output_file_name, f"{file_name_without_extension}_full.md")
        shutil.move(f"{file_name_without_extension}_0.md", output_file_name)
        print(
            f"The markdown file is too large for GitHub issue body and has been \
split into multiple files. ie. {output_file_name}, {file_name_without_extension}_1.md, etc. \
The full file is saved as {file_name_without_extension}_full.md\n"
        )


def main():  # pragma: no cover
    """
    Main function to run the innersource-measure tool.
    """

    print("Starting innersource-measure tool...")

    # Get the environment variables for use in the script
    env_vars = get_env_vars()
    token = env_vars.gh_token
    # report_title = env_vars.report_title
    # output_file = env_vars.output_file
    # rate_limit_bypass = env_vars.rate_limit_bypass

    ghe = env_vars.ghe
    gh_app_id = env_vars.gh_app_id
    gh_app_installation_id = env_vars.gh_app_installation_id
    gh_app_private_key_bytes = env_vars.gh_app_private_key_bytes
    gh_app_enterprise_only = env_vars.gh_app_enterprise_only

    # Auth to GitHub.com
    github_connection = auth_to_github(
        token,
        gh_app_id,
        gh_app_installation_id,
        gh_app_private_key_bytes,
        ghe,
        gh_app_enterprise_only,
    )

    if not token and gh_app_id and gh_app_installation_id and gh_app_private_key_bytes:
        token = get_github_app_installation_token(
            ghe, gh_app_id, gh_app_private_key_bytes, gh_app_installation_id
        )

    # evaluate_markdown_file_size(output_file)

    if github_connection:
        print("connection successful")


if __name__ == "__main__":
    main()
