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
from markdown_helpers import markdown_too_large_for_issue_body, split_markdown_file
from markdown_writer import write_to_markdown


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
    owner = env_vars.owner
    repo = env_vars.repo
    report_title = env_vars.report_title
    output_file = env_vars.output_file
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

        # fetch repository data
        print(f"Fetching repository data for {owner}/{repo}...")
        repo_data = github_connection.repository(owner, repo)
        if not repo_data:
            print(f"Unable to fetch repository {owner}/{repo} specified. Exiting.")
            return

        print(f"Repository {repo_data.full_name} found.")

        # Read in the org data in org-data.json
        org_data = None
        org_data_path = Path("org-data.json")
        if org_data_path.exists():
            print("Reading in org data from org-data.json...")
            with open(org_data_path, "r", encoding="utf-8") as org_file:
                org_data = json.load(org_file)
            print("Org data read successfully.")
        else:
            print("No org data found. InnerSource collaboration cannot be measured.")

        if org_data:
            print("Org data found. Measuring InnerSource collaboration...")
        else:
            print("No org data found. InnerSource collaboration cannot be measured.")
            return

        # Initialize contributor lists and team members list
        all_contributors = []
        innersource_contributors = []
        team_members_that_own_the_repo = []

        print("Analyzing first commit...")
        commits = repo_data.commits()
        # Paginate to the last page to get the oldest commit
        # commits is a GitHubIterator, so you can use .count to get total, then get the last one
        commit_list = list(commits)
        first_commit = commit_list[-1]  # The last in the list is the oldest
        original_commit_author = first_commit.author.login
        original_commit_author_manager = org_data[original_commit_author]["manager"]
        print(
            f"Original commit author: {original_commit_author}, \
with manager: {original_commit_author_manager}"
        )
        # Find all users that report up to the same manager as the original commit author
        team_members_that_own_the_repo.append(original_commit_author)
        team_members_that_own_the_repo.append(original_commit_author_manager)

        for user, data in org_data.items():
            if data["manager"] == original_commit_author_manager:
                team_members_that_own_the_repo.append(user)

        # for each username in team_members_that_own_the_repo,
        # add everyone that has one of them listed as the manager
        for user, data in org_data.items():
            if (
                user not in team_members_that_own_the_repo
                and data["manager"] in team_members_that_own_the_repo
            ):
                team_members_that_own_the_repo.append(user)

        # Remove duplicates from the team members list
        team_members_that_own_the_repo = list(set(team_members_that_own_the_repo))
        print(f"Team members that own the repo: {team_members_that_own_the_repo}")

        # For each contributor, check if they are in the team that owns the repo list
        # and if not, add them to the innersource contributors list
        print("Analyzing all contributors in the repository...")
        for contributor in repo_data.contributors():
            all_contributors.append(contributor.login)
            if (
                contributor.login not in team_members_that_own_the_repo
                and "[bot]" not in contributor.login
            ):
                innersource_contributors.append(contributor.login)

        print(f"All contributors: {all_contributors}")
        print(f"Innersource contributors: {innersource_contributors}")

        # Process data in chunks to avoid memory issues while maintaining performance
        chunk_size = env_vars.chunk_size
        print(f"Using chunk size of {chunk_size} for data processing")

        print("Pre-processing contribution data...")

        # Create mapping of commit authors to commit counts
        print("Processing commits...")
        commit_author_counts = {}
        for commit in commit_list:
            if hasattr(commit.author, "login"):
                author = commit.author.login
                commit_author_counts[author] = commit_author_counts.get(author, 0) + 1

        # Process pull requests in chunks
        print("Processing pull requests in chunks...")
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
            print(f"  Processed {total_prs} pull requests so far...")

        print(f"Found and processed {total_prs} pull requests")

        # Process issues in chunks
        print("Processing issues in chunks...")
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
            print(f"  Processed {total_issues} issues so far...")

        print(f"Found and processed {total_issues} issues")

        # Count contributions for each innersource contributor
        innersource_contribution_counts = {}
        print("Counting contributions for each innersource contributor...")
        for contributor in innersource_contributors:
            # Initialize counter for this contributor
            innersource_contribution_counts[contributor] = 0

            # Count commits by this contributor
            for commit in commit_list:
                if (
                    hasattr(commit.author, "login")
                    and commit.author.login == contributor
                ):
                    innersource_contribution_counts[contributor] += 1

            # Add PR and issue counts
            for pull in repo_data.pull_requests(state="all"):
                if pull.user.login == contributor:
                    innersource_contribution_counts[contributor] += 1

            for issue in repo_data.issues(state="all"):
                if hasattr(issue.user, "login") and issue.user.login == contributor:
                    innersource_contribution_counts[contributor] += 1

        print("Innersource contribution counts:")
        for contributor, count in innersource_contribution_counts.items():
            print(f"  {contributor}: {count} contributions")

        # count contributions for each user in team_members_that_own_the_repo
        team_member_contribution_counts = {}
        print("Counting contributions for each team member that owns the repo...")
        for member in team_members_that_own_the_repo:
            # Initialize counter for this team member
            team_member_contribution_counts[member] = 0

            # Count commits by this team member
            for commit in commit_list:
                if hasattr(commit.author, "login") and commit.author.login == member:
                    team_member_contribution_counts[member] += 1

            # Add PR and issue counts
            for pull in repo_data.pull_requests(state="all"):
                if pull.user.login == member:
                    team_member_contribution_counts[member] += 1

            for issue in repo_data.issues(state="all"):
                if hasattr(issue.user, "login") and issue.user.login == member:
                    team_member_contribution_counts[member] += 1

        print("Team member contribution counts:")
        for member, count in team_member_contribution_counts.items():
            if count > 0:
                print(f"  {member}: {count} contributions")

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

        print(f"Innersource contribution ratio: {innersource_ratio:.2%}")

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
        )

        evaluate_markdown_file_size(output_file)
        print(f"InnerSource report written to {output_file}")

    else:
        print("Failed to connect to GitHub. Exiting.")


if __name__ == "__main__":
    main()  # pragma: no cover
