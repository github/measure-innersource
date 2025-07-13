"""
Tests for markdown_writer.py specifically for the edge cases
"""

import os
import tempfile

from markdown_writer import write_to_markdown


class TestWriteToMarkdownEdgeCases:
    """
    Test cases for edge cases in markdown_writer.py
    """

    def test_write_to_markdown_empty_team_members(self):
        """
        Test writing markdown when team_members_that_own_the_repo is empty
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
                team_members_that_own_the_repo=None,  # Empty team members
                all_contributors=["contributor1"],
                innersource_contributors=["contributor1"],
                innersource_contribution_counts={"contributor1": 5},
                team_member_contribution_counts={"team_member1": 10},
            )

            # Read the generated file
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the "No team members available" message is included
            assert "No team members available." in content

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def test_write_to_markdown_empty_innersource_contributors(self):
        """
        Test writing markdown when innersource_contributors is empty
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
                innersource_contributors=None,  # Empty innersource contributors
                innersource_contribution_counts={"contributor1": 5},
                team_member_contribution_counts={"team_member1": 10},
            )

            # Read the generated file
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the "No InnerSource contributors found" message is included
            assert "No InnerSource contributors found." in content

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
