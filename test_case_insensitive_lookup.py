"""Unit tests for case-insensitive username lookup in org-data.json."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from measure_innersource import CaseInsensitiveDict, main


class TestCaseInsensitiveDict(unittest.TestCase):
    """Test suite for the CaseInsensitiveDict class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = {
            "alice": {"manager": "bob"},
            "Bob": {"manager": "charlie"},
            "Charlie": {"manager": "david"},
            "DAVID": {"manager": "eve"},
        }
        self.case_insensitive_dict = CaseInsensitiveDict(self.test_data)

    def test_getitem_lowercase_key(self):
        """Test getting an item with a lowercase key."""
        result = self.case_insensitive_dict["alice"]
        self.assertEqual(result, {"manager": "bob"})

    def test_getitem_uppercase_key(self):
        """Test getting an item with an uppercase key."""
        result = self.case_insensitive_dict["ALICE"]
        self.assertEqual(result, {"manager": "bob"})

    def test_getitem_mixedcase_key(self):
        """Test getting an item with a mixed case key."""
        result = self.case_insensitive_dict["Alice"]
        self.assertEqual(result, {"manager": "bob"})

    def test_getitem_original_case_preserved(self):
        """Test that original case in values is preserved."""
        result = self.case_insensitive_dict["bob"]
        self.assertEqual(result, {"manager": "charlie"})
        result = self.case_insensitive_dict["BOB"]
        self.assertEqual(result, {"manager": "charlie"})

    def test_getitem_key_not_found(self):
        """Test that KeyError is raised for missing keys."""
        with self.assertRaises(KeyError):
            _ = self.case_insensitive_dict["nonexistent"]

    def test_contains_lowercase(self):
        """Test __contains__ with lowercase key."""
        self.assertTrue("alice" in self.case_insensitive_dict)

    def test_contains_uppercase(self):
        """Test __contains__ with uppercase key."""
        self.assertTrue("ALICE" in self.case_insensitive_dict)

    def test_contains_mixedcase(self):
        """Test __contains__ with mixed case key."""
        self.assertTrue("Alice" in self.case_insensitive_dict)

    def test_contains_not_found(self):
        """Test __contains__ returns False for missing keys."""
        self.assertFalse("nonexistent" in self.case_insensitive_dict)

    def test_get_with_default(self):
        """Test get method with default value."""
        result = self.case_insensitive_dict.get("nonexistent", "default")
        self.assertEqual(result, "default")

    def test_get_without_default(self):
        """Test get method returns None if key not found and no default."""
        result = self.case_insensitive_dict.get("nonexistent")
        self.assertIsNone(result)

    def test_get_case_insensitive(self):
        """Test get method with case-insensitive key."""
        result = self.case_insensitive_dict.get("ALICE")
        self.assertEqual(result, {"manager": "bob"})

    def test_items(self):
        """Test items method returns original data."""
        items = list(self.case_insensitive_dict.items())
        self.assertEqual(len(items), 4)
        # Check that original keys are preserved
        keys = [k for k, v in items]
        self.assertIn("alice", keys)
        self.assertIn("Bob", keys)
        self.assertIn("Charlie", keys)
        self.assertIn("DAVID", keys)

    def test_keys(self):
        """Test keys method returns original keys."""
        keys = list(self.case_insensitive_dict.keys())
        self.assertEqual(len(keys), 4)
        self.assertIn("alice", keys)
        self.assertIn("Bob", keys)
        self.assertIn("Charlie", keys)
        self.assertIn("DAVID", keys)

    def test_values(self):
        """Test values method returns all values."""
        values = list(self.case_insensitive_dict.values())
        self.assertEqual(len(values), 4)

    def test_duplicate_case_insensitive_keys(self):
        """Test that ValueError is raised for duplicate case-insensitive keys."""
        duplicate_data = {
            "alice": {"manager": "bob"},
            "Alice": {"manager": "charlie"},  # Duplicate!
        }
        with self.assertRaises(ValueError) as context:
            CaseInsensitiveDict(duplicate_data)
        self.assertIn("Duplicate case-insensitive keys found", str(context.exception))
        self.assertIn("alice", str(context.exception).lower())


class TestCaseInsensitiveLookupIntegration(unittest.TestCase):
    """Integration tests for case-insensitive username lookup in measure_innersource."""

    @patch("measure_innersource.evaluate_markdown_file_size")
    @patch("measure_innersource.auth_to_github")
    @patch("measure_innersource.get_env_vars")
    @patch("measure_innersource.write_to_markdown")
    def test_username_lookup_case_insensitive(
        self,
        mock_write,
        mock_get_env_vars,
        mock_auth,
    ):
        """Test that username lookups in org-data.json are case-insensitive."""
        # Create a temporary org-data.json file with lowercase username
        org_data = {
            "jeffrey-luszcz": {"manager": "team-lead"},
            "team-lead": {"manager": "director"},
        }

        # Mock environment variables
        mock_env = MagicMock()
        mock_env.gh_token = "test_token"
        mock_env.owner = "test_owner"
        mock_env.repo = "test_repo"
        mock_env.report_title = "Test Report"
        mock_env.output_file = "test_output.md"
        mock_env.ghe = ""
        mock_env.gh_app_id = None
        mock_env.gh_app_installation_id = None
        mock_env.gh_app_private_key_bytes = None
        mock_env.gh_app_enterprise_only = False
        mock_env.chunk_size = 100
        mock_get_env_vars.return_value = mock_env

        # Mock GitHub connection and repository
        mock_github = MagicMock()
        mock_auth.return_value = mock_github

        mock_repo = MagicMock()
        mock_github.repository.return_value = mock_repo
        mock_repo.full_name = "test_owner/test_repo"

        # Mock first commit with different case username
        mock_commit = MagicMock()
        mock_commit.author.login = "Jeffrey-Luszcz"  # Different case!
        mock_repo.commits.return_value = [mock_commit]

        # Mock contributors with different case
        mock_contributor = MagicMock()
        mock_contributor.login = "Jeffrey-Luszcz"
        mock_repo.contributors.return_value = [mock_contributor]

        # Mock PRs and issues (empty for simplicity)
        mock_repo.pull_requests.return_value = iter([])
        mock_repo.issues.return_value = iter([])

        # Create temp directory for org-data.json
        with tempfile.TemporaryDirectory() as tmpdir:
            org_data_path = Path(tmpdir) / "org-data.json"
            with open(org_data_path, "w", encoding="utf-8") as f:
                json.dump(org_data, f)

            # Change to temp directory and run test
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)

                # Run main
                main()

                # Verify that write_to_markdown was called (meaning no KeyError occurred)
                mock_write.assert_called_once()

                # Get the arguments passed to write_to_markdown
                call_args = mock_write.call_args
                kwargs = call_args.kwargs if call_args.kwargs else {}

                # Verify the original commit author is correctly identified
                self.assertEqual(kwargs.get("original_commit_author"), "Jeffrey-Luszcz")
                # Verify the manager was looked up correctly (case-insensitive)
                self.assertEqual(
                    kwargs.get("original_commit_author_manager"), "team-lead"
                )

            finally:
                os.chdir(original_dir)


if __name__ == "__main__":
    unittest.main()
