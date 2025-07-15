"""Markdown report generation module for InnerSource collaboration analysis.

This module provides functionality to generate comprehensive markdown reports that
analyze InnerSource collaboration within GitHub repositories. The reports include
detailed information about team ownership, contributor analysis, and contribution
statistics.

The generated reports help organizations understand:
- How much cross-team collaboration is happening in their repositories
- Who are the key InnerSource contributors from outside teams
- The ratio of InnerSource contributions to total contributions
- Team boundaries and ownership patterns

Report Structure:
    The generated markdown reports include:
    1. Repository identification and metadata
    2. InnerSource collaboration ratio calculations
    3. Original commit author and team ownership information
    4. Complete contributor lists and categorization
    5. Detailed contribution counts and statistics

Functions:
    write_to_markdown: Generate a complete InnerSource collaboration report

Dependencies:
    - Standard library file operations for markdown generation
    - GitHub API data structures for repository information
"""


def write_to_markdown(
    report_title="",
    output_file="",
    innersource_ratio=None,
    repo_data=None,
    original_commit_author="",
    original_commit_author_manager="",
    team_members_that_own_the_repo=None,
    all_contributors=None,
    innersource_contributors=None,
    innersource_contribution_counts=None,
    team_member_contribution_counts=None,
) -> None:
    """
    Generate a comprehensive InnerSource collaboration report in markdown format.

    This function creates a detailed markdown report that analyzes InnerSource collaboration
    within a repository. The report includes team ownership information, contributor
    analysis, and contribution statistics.

    Args:
        report_title (str, optional): The title to display at the top of the report.
                                     Defaults to empty string.
        output_file (str, optional): The filename for the output markdown file.
                                    Defaults to "innersource_report.md" if empty.
        innersource_ratio (float | None, optional): The calculated ratio of InnerSource
                                                   contributions to total contributions.
                                                   Should be a float between 0 and 1.
        repo_data (github3.repos.Repository | None, optional): The GitHub repository
                                                               object containing repository
                                                               metadata. If None, generates
                                                               a minimal report.
        original_commit_author (str, optional): The username of the author of the
                                               repository's first commit. Used to
                                               determine repository ownership.
        original_commit_author_manager (str, optional): The manager of the original
                                                        commit author, used for team
                                                        boundary determination.
        team_members_that_own_the_repo (list[str] | None, optional): List of usernames
                                                                     who are considered
                                                                     owners of the repository.
        all_contributors (list[str] | None, optional): List of all contributor usernames
                                                       who have made contributions to
                                                       the repository.
        innersource_contributors (list[str] | None, optional): List of contributor
                                                              usernames who are from
                                                              outside the owning team.
        innersource_contribution_counts (dict[str, int] | None, optional): Dictionary
                                                                           mapping InnerSource
                                                                           contributor usernames
                                                                           to their contribution
                                                                           counts.
        team_member_contribution_counts (dict[str, int] | None, optional): Dictionary
                                                                           mapping team member
                                                                           usernames to their
                                                                           contribution counts.

    Returns:
        None: This function creates a markdown file as a side effect.

    Side Effects:
        - Creates a markdown file with the specified filename
        - Overwrites the file if it already exists
        - Writes UTF-8 encoded content

    Report Structure:
        The generated report includes the following sections:
        1. Report title
        2. Repository information
        3. InnerSource ratio calculation
        4. Original commit author and manager
        5. Team members who own the repository
        6. All contributors list
        7. InnerSource contributors list
        8. InnerSource contribution counts
        9. Team member contribution counts

    Examples:
        >>> # Generate a basic report
        >>> write_to_markdown(
        ...     report_title="My Repository InnerSource Report",
        ...     output_file="my_report.md",
        ...     innersource_ratio=0.35,
        ...     repo_data=repo_object
        ... )

        >>> # Generate a complete report with all data
        >>> write_to_markdown(
        ...     report_title="Complete Analysis",
        ...     output_file="analysis.md",
        ...     innersource_ratio=0.42,
        ...     repo_data=repo_object,
        ...     original_commit_author="alice",
        ...     original_commit_author_manager="bob",
        ...     team_members_that_own_the_repo=["alice", "bob", "charlie"],
        ...     all_contributors=["alice", "bob", "charlie", "dave", "eve"],
        ...     innersource_contributors=["dave", "eve"],
        ...     innersource_contribution_counts={"dave": 15, "eve": 8},
        ...     team_member_contribution_counts={"alice": 25, "bob": 12, "charlie": 5}
        ... )
    """
    output_file_name = output_file if output_file else "innersource_report.md"
    with open(output_file_name, "w", encoding="utf-8") as report_file:
        report_file.write(f"# {report_title}\n\n")
        # Check if repo_data is None to handle test cases
        if repo_data is None:
            report_file.write("no op\n\n")
            return
        report_file.write(f"## Repository: {repo_data.full_name}\n\n")
        report_file.write(f"### InnerSource Ratio: {innersource_ratio:.2%}\n\n")
        report_file.write(
            f"### Original Commit Author: {original_commit_author} (Manager: {original_commit_author_manager})\n\n"
        )
        report_file.write("## Team Members that Own the Repo:\n")
        if team_members_that_own_the_repo:
            for member in team_members_that_own_the_repo:
                report_file.write(f"- {member}\n")
        else:
            report_file.write("No team members available.\n")

        report_file.write("\n## All Contributors:\n")
        if all_contributors:
            for contributor in all_contributors:
                report_file.write(f"- {contributor}\n")
        else:
            report_file.write("No contributors found.\n")

        report_file.write("\n## Innersource Contributors:\n")
        if innersource_contributors:
            for contributor in innersource_contributors:
                report_file.write(f"- {contributor}\n")
        else:
            report_file.write("No InnerSource contributors found.\n")

        report_file.write("\n## Innersource Contribution Counts:\n")
        if innersource_contribution_counts:
            for contributor, count in innersource_contribution_counts.items():
                report_file.write(f"- {contributor}: {count} contributions\n")
        else:
            report_file.write("No InnerSource contribution counts available.\n")

        report_file.write("\n## Team Member Contribution Counts:\n")
        if team_member_contribution_counts:
            found_contributions = False
            for member, count in team_member_contribution_counts.items():
                if count > 0:
                    found_contributions = True
                    report_file.write(f"- {member}: {count} contributions\n")
            if not found_contributions:
                report_file.write("No team member contributions found.\n")
        else:
            report_file.write("No team member contribution counts available.\n")
