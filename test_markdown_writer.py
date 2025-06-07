"""A module containing unit tests for the write_to_markdown function in the markdown_writer module.

Classes:
    TestWriteToMarkdown: A class to test the write_to_markdown function with mock data.

"""

import os
import unittest
from unittest.mock import patch

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

    def test_write_to_markdown(self):
        """Test that write_to_markdown writes the correct markdown file.

        This test creates a list of mock GitHub issues with time to first response
        attributes, calls write_to_markdown with the list and the average time to
        first response, time to close and checks that the function writes the correct
        markdown file.

        """
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
