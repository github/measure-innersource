"""
Tests for markdown_writer.py specifically for when only original_commit_author is provided
"""

import os
import tempfile

from markdown_writer import write_to_markdown


def test_write_to_markdown_original_author_only():
    """
    Test writing markdown when only original_commit_author is provided without manager
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
            original_commit_author="author",  # Only provide the author, not the manager
            original_commit_author_manager="",  # Empty manager
            team_members_that_own_the_repo=["team_member1"],
            all_contributors=["contributor1"],
            innersource_contributors=["contributor1"],
            innersource_contribution_counts={"contributor1": 5},
            team_member_contribution_counts={"team_member1": 10},
            team_ownership_explicitly_specified=False,
        )

        # Read the generated file
        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that the original author is included without manager
        assert "### Original Commit Author: author\n" in content

        # Make sure the manager version is not included
        assert "Manager:" not in content

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
