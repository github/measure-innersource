"""A tool for measuring InnerSource collaboration in a given repository

This script uses the GitHub API to search for issues/prs in a repository
and measure the InnerSource collaboration occuring in those issues/prs.
The results are then written to a markdown file.

"""

import json
import shutil
from pathlib import Path

from auth import auth_to_github, get_github_app_installation_token
from config import get_env_vars
from constants import GITHUB_ISSUE_BODY_MAX_CHARS
from logging_config import get_logger, setup_logging
from markdown_helpers import markdown_too_large_for_issue_body, split_markdown_file
from markdown_writer import write_to_markdown


def evaluate_markdown_file_size(output_file: str) -> None:
    """
    Evaluate the size of the markdown file and split it if it exceeds GitHub's issue body limits.

    This function checks if the generated markdown report is too large for GitHub issues
    (which have a 65,535 character limit) and splits it into multiple files if necessary.

    Args:
        output_file (str): The name of the output markdown file to evaluate.
                          If empty or None, defaults to "innersource_report.md".

    Returns:
        None: This function performs file operations and prints status messages.

    Side Effects:
        - Creates additional markdown files if splitting is needed
        - Renames the original file to {filename}_full.md
        - Moves the first split file to the original filename
        - Prints informational messages about the splitting process
    """
    output_file_name = output_file if output_file else "innersource_report.md"
    file_name_without_extension = Path(output_file_name).stem
    max_char_count = GITHUB_ISSUE_BODY_MAX_CHARS
    logger = get_logger()

    if markdown_too_large_for_issue_body(output_file_name, max_char_count):
        split_markdown_file(output_file_name, max_char_count)
        shutil.move(output_file_name, f"{file_name_without_extension}_full.md")
        shutil.move(f"{file_name_without_extension}_0.md", output_file_name)
        logger.info(
            "The markdown file is too large for GitHub issue body and has been "
            "split into multiple files. ie. %s, %s_1.md, etc. "
            "The full file is saved as %s_full.md\n",
            output_file_name,
            file_name_without_extension,
            file_name_without_extension,
        )


def main():  # pragma: no cover
    """
    Main function to run the InnerSource measurement tool.

    This function orchestrates the entire InnerSource measurement process:
    1. Loads environment variables and configuration
    2. Authenticates to GitHub (using either PAT or GitHub App)
    3. Fetches repository data and organizational information
    4. Analyzes contributors and their relationships to determine team boundaries
    5. Processes commits, pull requests, and issues to count contributions
    6. Calculates InnerSource collaboration ratios
    7. Generates a comprehensive markdown report

    The function uses chunked processing to handle large repositories efficiently
    and memory-safely.

    Returns:
        None: This function performs the main application logic and generates
              output files and console messages.

    Raises:
        Various exceptions may be raised during GitHub API calls, file operations,
        or data processing. These are generally handled gracefully with informative
        error messages.

    Side Effects:
        - Writes a markdown report to the specified output file
        - Prints progress messages to the console
        - May create additional split files for large reports
        - Requires org-data.json file to be present in the current directory
    """

    # Initialize logging
    logger = setup_logging()
    logger.info("Starting innersource-measure tool...")

    # Get the environment variables for use in the script
    env_vars = get_env_vars()
    token = env_vars.gh_token
    owner = env_vars.owner
    repo = env_vars.repo
    report_title = env_vars.report_title
    output_file = env_vars.output_file
    owning_team = env_vars.owning_team
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

    if github_connection:
        logger.info("Connection to GitHub successful")

        # fetch repository data
        logger.info("Fetching repository data for %s/%s...", owner, repo)
        repo_data = github_connection.repository(owner, repo)
        if not repo_data:
            logger.error(
                "Unable to fetch repository %s/%s specified. Exiting.", owner, repo
            )
            return

        logger.info("Repository %s found.", repo_data.full_name)

        # Read in the org data in org-data.json
        org_data = None
        org_data_path = Path("org-data.json")
        if org_data_path.exists():
            logger.info("Reading in org data from org-data.json...")
            with open(org_data_path, "r", encoding="utf-8") as org_file:
                org_data = json.load(org_file)
            logger.info("Org data read successfully.")
        else:
            logger.warning(
                "No org data found. InnerSource collaboration cannot be measured."
            )

        if org_data:
            logger.info("Org data found. Measuring InnerSource collaboration...")
        else:
            logger.error(
                "No org data found. InnerSource collaboration cannot be measured."
            )
            return

        # Initialize contributor lists and team members list
        all_contributors = []
        innersource_contributors = []
        team_members_that_own_the_repo = []

        # Get all commits for contribution counting (needed regardless of team determination method)
        logger.info("Fetching commits...")
        commits = repo_data.commits()
        commit_list = list(commits)

        # Check if owning team is explicitly specified
        if owning_team:
            logger.info("Using explicitly specified owning team: %s", owning_team)
            team_members_that_own_the_repo = owning_team
            # Set variables to None since they're not used when team is specified
            original_commit_author = None
            original_commit_author_manager = None
        else:
            logger.info("Analyzing first commit...")
            # Paginate to the last page to get the oldest commit
            # commits is a GitHubIterator, so you can use .count to get total,
            # then get the last one
            first_commit = commit_list[-1]  # The last in the list is the oldest
            original_commit_author = first_commit.author.login

            # Check if original commit author exists in org chart
            if original_commit_author not in org_data:
                logger.warning(
                    "Original commit author '%s' not found in org chart. "
                    "Cannot determine team boundaries for InnerSource "
                    "measurement.",
                    original_commit_author,
                )
                return

            original_commit_author_manager = org_data[original_commit_author]["manager"]
            logger.info(
                "Original commit author: %s, with manager: %s",
                original_commit_author,
                original_commit_author_manager,
            )
            # Create a dictionary mapping users to their managers for faster lookups
            user_to_manager = {}
            manager_to_reports = {}

            for user, data in org_data.items():
                manager = data["manager"]
                user_to_manager[user] = manager

                # Also create reverse mapping of manager to direct reports
                if manager not in manager_to_reports:
                    manager_to_reports[manager] = []
                manager_to_reports[manager].append(user)

            # Find all users that report up to the same manager as the original commit author
            team_members_that_own_the_repo.append(original_commit_author)
            team_members_that_own_the_repo.append(original_commit_author_manager)

            # Add all users reporting to the same manager
            if original_commit_author_manager in manager_to_reports:
                team_members_that_own_the_repo.extend(
                    manager_to_reports[original_commit_author_manager]
                )

            # Add everyone that has one of the team members listed as their manager
            for user, manager in user_to_manager.items():
                if (
                    manager in team_members_that_own_the_repo
                    and user not in team_members_that_own_the_repo
                ):
                    team_members_that_own_the_repo.append(user)

            # Remove duplicates from the team members list
            team_members_that_own_the_repo = list(set(team_members_that_own_the_repo))
            logger.debug(
                "Team members that own the repo: %s", team_members_that_own_the_repo
            )

        # For each contributor, check if they are in the team that owns the repo list
        # and if not, add them to the innersource contributors list
        logger.info("Analyzing all contributors in the repository...")
        for contributor in repo_data.contributors():
            all_contributors.append(contributor.login)

            # Check if contributor is not found in org chart
            if contributor.login not in org_data:
                logger.warning(
                    "Contributor '%s' not found in org chart. "
                    "Excluding from InnerSource analysis.",
                    contributor.login,
                )
                continue

            if (
                contributor.login not in team_members_that_own_the_repo
                and "[bot]" not in contributor.login
            ):
                innersource_contributors.append(contributor.login)

        logger.debug("All contributors: %s", all_contributors)
        logger.debug("Innersource contributors: %s", innersource_contributors)

        # Process data in chunks to avoid memory issues while maintaining performance
        chunk_size = env_vars.chunk_size
        logger.info("Using chunk size of %s for data processing", chunk_size)

        logger.info("Pre-processing contribution data...")

        # Create mapping of commit authors to commit counts
        logger.info("Processing commits...")
        commit_author_counts = {}
        for commit in commit_list:
            if hasattr(commit.author, "login"):
                author = commit.author.login
                commit_author_counts[author] = commit_author_counts.get(author, 0) + 1

        # Process pull requests in chunks
        logger.info("Processing pull requests in chunks...")
        pr_author_counts = {}
        total_prs = 0

        # GitHub API returns an iterator that internally handles pagination
        # We'll manually chunk it to avoid loading everything at once
        pulls_iterator = repo_data.pull_requests(state="all")
        while True:
            # Process a chunk of pull requests
            chunk = []
            for _ in range(chunk_size):
                try:
                    chunk.append(next(pulls_iterator))
                except StopIteration:
                    break

            if not chunk:
                break

            # Update counts for this chunk
            for pull in chunk:
                if hasattr(pull.user, "login"):
                    author = pull.user.login
                    pr_author_counts[author] = pr_author_counts.get(author, 0) + 1

            total_prs += len(chunk)
            logger.debug("  Processed %s pull requests so far...", total_prs)

        logger.info("Found and processed %s pull requests", total_prs)

        # Process issues in chunks
        logger.info("Processing issues in chunks...")
        issue_author_counts = {}
        total_issues = 0

        # GitHub API returns an iterator that internally handles pagination
        # We'll manually chunk it to avoid loading everything at once
        issues_iterator = repo_data.issues(state="all")
        while True:
            # Process a chunk of issues
            chunk = []
            for _ in range(chunk_size):
                try:
                    chunk.append(next(issues_iterator))
                except StopIteration:
                    break

            if not chunk:
                break

            # Update counts for this chunk
            for issue in chunk:
                if hasattr(issue.user, "login"):
                    author = issue.user.login
                    issue_author_counts[author] = issue_author_counts.get(author, 0) + 1

            total_issues += len(chunk)
            logger.debug("  Processed %s issues so far...", total_issues)

        logger.info("Found and processed %s issues", total_issues)

        # Count contributions for each innersource contributor using precompiled dictionaries
        innersource_contribution_counts = {}
        logger.info("Counting contributions for each innersource contributor...")
        for contributor in innersource_contributors:
            # Initialize counter for this contributor
            innersource_contribution_counts[contributor] = 0

            # Add commit counts from the precompiled dictionary
            innersource_contribution_counts[contributor] += commit_author_counts.get(
                contributor, 0
            )

            # Add PR counts from the precompiled dictionary
            innersource_contribution_counts[contributor] += pr_author_counts.get(
                contributor, 0
            )

            # Add issue counts from the precompiled dictionary
            innersource_contribution_counts[contributor] += issue_author_counts.get(
                contributor, 0
            )

        logger.debug("Innersource contribution counts:")
        for contributor, count in innersource_contribution_counts.items():
            logger.debug("  %s: %s contributions", contributor, count)

        # Count contributions for each team member using precompiled dictionaries
        team_member_contribution_counts = {}
        logger.info("Counting contributions for each team member that owns the repo...")
        for member in team_members_that_own_the_repo:
            # Initialize counter for this team member
            team_member_contribution_counts[member] = 0

            # Add commit counts from the precompiled dictionary
            team_member_contribution_counts[member] += commit_author_counts.get(
                member, 0
            )

            # Add PR counts from the precompiled dictionary
            team_member_contribution_counts[member] += pr_author_counts.get(member, 0)

            # Add issue counts from the precompiled dictionary
            team_member_contribution_counts[member] += issue_author_counts.get(
                member, 0
            )

        logger.debug("Team member contribution counts:")
        for member, count in team_member_contribution_counts.items():
            if count > 0:
                logger.debug("  %s: %s contributions", member, count)

        # Calculate the ratio of innersource contributions to total contributions
        total_contributions = sum(innersource_contribution_counts.values()) + sum(
            team_member_contribution_counts.values()
        )
        if total_contributions > 0:
            innersource_ratio = (
                sum(innersource_contribution_counts.values()) / total_contributions
            )
        else:
            innersource_ratio = 0

        logger.info("Innersource contribution ratio: %.2f%%", innersource_ratio * 100)

        # Write the results to a markdown file using report_title and output_file
        write_to_markdown(
            report_title=report_title,
            output_file=output_file,
            innersource_ratio=innersource_ratio,
            repo_data=repo_data,
            original_commit_author=original_commit_author,
            original_commit_author_manager=original_commit_author_manager,
            team_members_that_own_the_repo=team_members_that_own_the_repo,
            all_contributors=all_contributors,
            innersource_contributors=innersource_contributors,
            innersource_contribution_counts=innersource_contribution_counts,
            team_member_contribution_counts=team_member_contribution_counts,
            team_ownership_explicitly_specified=bool(
                owning_team
            ),  # True if owning_team is specified
        )

        evaluate_markdown_file_size(output_file)
        logger.info("InnerSource report written to %s", output_file)

    else:
        logger.error("Failed to connect to GitHub. Exiting.")


if __name__ == "__main__":
    main()  # pragma: no cover
