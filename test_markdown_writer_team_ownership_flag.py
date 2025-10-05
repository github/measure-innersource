"""
Tests for markdown_writer.py specifically for the team_ownership_explicitly_specified parameter
"""

import os
import tempfile

from markdown_writer import write_to_markdown


def test_write_to_markdown_missing_original_author_with_flag():
    """
    Test writing markdown with team_ownership_explicitly_specified=True
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

        # Test with missing original author but with explicit team ownership flag
        write_to_markdown(
            report_title="Test Report",
            output_file=temp_file_path,
            innersource_ratio=0.5,
            repo_data=MockRepo(),
            original_commit_author=None,  # No original author
            original_commit_author_manager=None,  # No manager
            team_members_that_own_the_repo=["team_member1"],
            all_contributors=["contributor1"],
            innersource_contributors=["contributor1"],
            innersource_contribution_counts={"contributor1": 5},
            team_member_contribution_counts={"team_member1": 10},
            team_ownership_explicitly_specified=True,  # Explicit flag
        )

        # Read the generated file
        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that explicit team ownership message is included
        assert "### Team ownership is explicitly specified" in content
        # Make sure the "Original commit author information not available" is not included
        assert "Original commit author information not available" not in content

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_write_to_markdown_missing_original_author_without_flag():
    """
    Test writing markdown with missing original_commit_author but without team_ownership_explicitly_specified
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

        # Test with missing original author and without explicit team ownership flag
        write_to_markdown(
            report_title="Test Report",
            output_file=temp_file_path,
            innersource_ratio=0.5,
            repo_data=MockRepo(),
            original_commit_author=None,  # No original author
            original_commit_author_manager=None,  # No manager
            team_members_that_own_the_repo=["team_member1"],
            all_contributors=["contributor1"],
            innersource_contributors=["contributor1"],
            innersource_contribution_counts={"contributor1": 5},
            team_member_contribution_counts={"team_member1": 10},
            team_ownership_explicitly_specified=False,  # Flag is False
        )

        # Read the generated file
        with open(temp_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that "Original commit author information not available" is included
        assert "### Original commit author information not available" in content
        # Make sure the team ownership explicitly specified message is not included
        assert "Team ownership is explicitly specified" not in content

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
