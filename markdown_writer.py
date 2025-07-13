"""
A module for writing an InnerSource Report to a markdown file.
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
    Write an InnerSource Report to a markdown file.
    Args:
        report_title (str): The title of the report.
        output_file (str): The name of the output markdown file.
        innersource_ratio (float): The ratio of InnerSource contributions.
        repo_data (object): The repository data object.
        original_commit_author (str): The original commit author's name.
        original_commit_author_manager (str): The manager of the original commit author.
        team_members_that_own_the_repo (list): List of team members that own the repository.
        all_contributors (list): List of all contributors to the repository.
        innersource_contributors (list): List of InnerSource contributors.
        innersource_contribution_counts (dict): Dictionary of InnerSource contribution counts.
        team_member_contribution_counts (dict): Dictionary of team member contribution counts.

    Returns:
        None
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
