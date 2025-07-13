"""A module containing unit tests for the write_to_markdown function in the markdown_writer module.

Classes:
    TestWriteToMarkdown: A class to test the write_to_markdown function with mock data.

"""

import os
import unittest
from unittest.mock import MagicMock, patch

from markdown_writer import write_to_markdown


@patch.dict(
    os.environ,
    {
        "GH_TOKEN": "test_token",
    },
)
class TestWriteToMarkdown(unittest.TestCase):
    """Test the write_to_markdown function."""

    maxDiff = None

    def test_write_to_markdown_no_repo_data(self):
        """Test that write_to_markdown handles the case when repo_data is None."""
        # Call the function
        write_to_markdown(
            report_title="InnerSource Report",
            output_file="innersource_report.md",
        )

        # Check that the function writes the correct markdown file
        with open("innersource_report.md", "r", encoding="utf-8") as file:
            content = file.read()
        expected_content = "# InnerSource Report\n\nno op\n\n"
        self.assertEqual(content, expected_content)
        os.remove("innersource_report.md")

    def test_write_to_markdown_with_data(self):
        """Test that write_to_markdown writes the correct markdown file with all data."""
        # Create mock data
        mock_repo = MagicMock()
        mock_repo.full_name = "owner/repo"

        team_members = ["member1", "member2"]
        all_contributors = ["member1", "member2", "contributor1"]
        innersource_contributors = ["contributor1"]
        innersource_counts = {"contributor1": 5}
        team_member_counts = {"member1": 10, "member2": 0}

        # Call the function
        write_to_markdown(
            report_title="InnerSource Report",
            output_file="innersource_report_full.md",
            innersource_ratio=0.25,
            repo_data=mock_repo,
            original_commit_author="member1",
            original_commit_author_manager="manager1",
            team_members_that_own_the_repo=team_members,
            all_contributors=all_contributors,
            innersource_contributors=innersource_contributors,
            innersource_contribution_counts=innersource_counts,
            team_member_contribution_counts=team_member_counts,
        )

        # Check that the function writes the correct markdown file
        with open("innersource_report_full.md", "r", encoding="utf-8") as file:
            content = file.read()

        # Verify the content contains all sections
        self.assertIn("# InnerSource Report", content)
        self.assertIn("## Repository: owner/repo", content)
        self.assertIn("### InnerSource Ratio: 25.00%", content)
        self.assertIn(
            "### Original Commit Author: member1 (Manager: manager1)", content
        )
        self.assertIn("## Team Members that Own the Repo:", content)
        self.assertIn("- member1", content)
        self.assertIn("- member2", content)
        self.assertIn("## All Contributors:", content)
        self.assertIn("## Innersource Contributors:", content)
        self.assertIn("- contributor1", content)
        self.assertIn("## Innersource Contribution Counts:", content)
        self.assertIn("- contributor1: 5 contributions", content)
        self.assertIn("## Team Member Contribution Counts:", content)
        self.assertIn("- member1: 10 contributions", content)
        self.assertNotIn(
            "- member2: 0 contributions", content
        )  # Should not include zero counts

        os.remove("innersource_report_full.md")

    def test_write_to_markdown_default_filename(self):
        """Test that write_to_markdown uses the default filename when none is provided."""
        # Call the function with no output_file
        write_to_markdown(
            report_title="InnerSource Report",
        )

        # Check that the function uses the default filename
        self.assertTrue(os.path.exists("innersource_report.md"))
        os.remove("innersource_report.md")
