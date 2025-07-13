"""
Tests for markdown_writer.py specifically for zero contribution counts
"""

import os
import tempfile

from markdown_writer import write_to_markdown


class TestWriteToMarkdownZeroContributions:
    """
    Test cases for zero contributions in markdown_writer.py
    """

    def test_write_to_markdown_zero_contributions(self):
        """
        Test writing markdown when team_member_contribution_counts has only zeros
        """
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Mock repo data object
            class MockRepo:
                """
                Mock repository data class for testing
                """

                @property
                def full_name(self):
                    """
                    Returns the full name of the mock repository
                    """
                    return "owner/repo"

            write_to_markdown(
                report_title="Test Report",
                output_file=temp_file_path,
                innersource_ratio=0.5,
                repo_data=MockRepo(),
                original_commit_author="author",
                original_commit_author_manager="manager",
                team_members_that_own_the_repo=["team_member1"],
                all_contributors=["contributor1"],
                innersource_contributors=["contributor1"],
                innersource_contribution_counts={"contributor1": 5},
                team_member_contribution_counts={
                    "team_member1": 0,
                    "team_member2": 0,
                },  # All zero counts
            )

            # Read the generated file
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the "No team member contributions found" message is included
            assert "No team member contributions found." in content

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
