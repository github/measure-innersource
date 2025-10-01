"""Unit tests for OWNING_TEAM environment variable in config module."""

import os
import unittest
from unittest.mock import patch

from config import get_env_vars


class TestOwningTeamEnvVar(unittest.TestCase):
    """Test suite for the OWNING_TEAM environment variable."""

    def setUp(self):
        """Clean up environment before each test."""
        env_keys = [
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GH_TOKEN",
            "GH_ENTERPRISE_URL",
            "OUTPUT_FILE",
            "REPORT_TITLE",
            "RATE_LIMIT_BYPASS",
            "REPOSITORY",
            "OWNING_TEAM",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": "alice,bob,charlie",
        },
    )
    def test_owning_team_parsed_correctly(self):
        """Test that OWNING_TEAM is parsed correctly as a list."""
        env_vars = get_env_vars(test=True)
        self.assertIsNotNone(env_vars.owning_team)
        self.assertEqual(env_vars.owning_team, ["alice", "bob", "charlie"])

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": "alice, bob, charlie",
        },
    )
    def test_owning_team_with_spaces(self):
        """Test that OWNING_TEAM handles spaces correctly."""
        env_vars = get_env_vars(test=True)
        self.assertIsNotNone(env_vars.owning_team)
        self.assertEqual(env_vars.owning_team, ["alice", "bob", "charlie"])

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": "single-user",
        },
    )
    def test_owning_team_single_user(self):
        """Test that OWNING_TEAM works with a single user."""
        env_vars = get_env_vars(test=True)
        self.assertIsNotNone(env_vars.owning_team)
        self.assertEqual(env_vars.owning_team, ["single-user"])

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": "",
        },
    )
    def test_owning_team_empty_string(self):
        """Test that empty OWNING_TEAM is treated as None."""
        env_vars = get_env_vars(test=True)
        self.assertIsNone(env_vars.owning_team)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
        },
    )
    def test_owning_team_not_set(self):
        """Test that missing OWNING_TEAM is None."""
        env_vars = get_env_vars(test=True)
        self.assertIsNone(env_vars.owning_team)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": " , , ",
        },
    )
    def test_owning_team_only_spaces_and_commas(self):
        """Test that OWNING_TEAM with only spaces and commas is treated as None."""
        env_vars = get_env_vars(test=True)
        self.assertIsNone(env_vars.owning_team)

    @patch.dict(
        os.environ,
        {
            "GH_TOKEN": "test_token",
            "REPOSITORY": "owner/repo",
            "OWNING_TEAM": "alice,,bob,,,charlie",
        },
    )
    def test_owning_team_with_empty_entries(self):
        """Test that OWNING_TEAM handles empty entries correctly."""
        env_vars = get_env_vars(test=True)
        self.assertIsNotNone(env_vars.owning_team)
        # Empty entries should be filtered out
        self.assertEqual(env_vars.owning_team, ["alice", "bob", "charlie"])


if __name__ == "__main__":
    unittest.main()
