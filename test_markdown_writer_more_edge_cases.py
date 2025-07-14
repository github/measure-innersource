"""
Tests for markdown_writer.py specifically for the edge cases - additional tests
"""

import os
import tempfile

from markdown_writer import write_to_markdown


class TestWriteToMarkdownMoreEdgeCases:
    """
    Additional test cases for edge cases in markdown_writer.py
    """

    def test_write_to_markdown_empty_all_values(self):
        """
        Test writing markdown when all collections are empty
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
                team_members_that_own_the_repo=["member1"],
                all_contributors=None,  # Empty all contributors
                innersource_contributors=["contributor1"],
                innersource_contribution_counts=None,  # Empty contribution counts
                team_member_contribution_counts={},  # Empty dict for team member counts
            )

            # Read the generated file
            with open(temp_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for expected messages
            assert "No contributors found" in content
            assert "No InnerSource contribution counts available" in content
            assert "No team member contribution counts available" in content

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
