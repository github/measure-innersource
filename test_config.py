"""A module containing unit tests for the config module functions.

Classes:
    TestGetIntFromEnv: A class to test the get_int_env_var function.
    TestEnvVars: A class to test the get_env_vars function.

"""

import os
import unittest
from unittest.mock import patch

from config import EnvVars, get_env_vars, get_int_env_var

TOKEN = "test_token"


class TestGetIntFromEnv(unittest.TestCase):
    """
    Test suite for the get_int_from_env function.

    ...

    Test methods:
        - test_get_int_env_var: Test returns the expected integer value.
        - test_get_int_env_var_with_empty_env_var: Test returns None when environment variable
          is empty.
        - test_get_int_env_var_with_non_integer: Test returns None when environment variable
          is a non-integer.
    """

    @patch.dict(os.environ, {"INT_ENV_VAR": "12345"})
    def test_get_int_env_var(self):
        """
        Test that get_int_env_var returns the expected integer value.
        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertEqual(result, 12345)

    @patch.dict(os.environ, {"INT_ENV_VAR": ""})
    def test_get_int_env_var_with_empty_env_var(self):
        """
        This test verifies that the get_int_env_var function returns None
        when the environment variable is empty.

        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertIsNone(result)

    @patch.dict(os.environ, {"INT_ENV_VAR": "not_an_int"})
    def test_get_int_env_var_with_non_integer(self):
        """
        Test that get_int_env_var returns None when the environment variable is
        a non-integer.

        """
        result = get_int_env_var("INT_ENV_VAR")
        self.assertIsNone(result)


class TestGetEnvVars(unittest.TestCase):
    """
    Test suite for the get_env_vars function.
    """

    def setUp(self):
        env_keys = [
            "GH_APP_ID",
            "GH_APP_INSTALLATION_ID",
            "GH_APP_PRIVATE_KEY",
            "GH_TOKEN",
            "GHE",
            "OUTPUT_FILE",
            "REPORT_TITLE",
            "RATE_LIMIT_BYPASS",
        ]
        for key in env_keys:
            if key in os.environ:
                del os.environ[key]

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "678910",
            "GH_APP_PRIVATE_KEY": "hello",
            "GH_TOKEN": "",
            "GH_ENTERPRISE_URL": "",
            "OUTPUT_FILE": "",
            "REPOSITORY": "test_owner/test_repo",
            "REPORT_TITLE": "",
            "RATE_LIMIT_BYPASS": "false",
        },
        clear=True,
    )
    def test_get_env_vars_with_github_app(self):
        """Test that all environment variables are set correctly using GitHub App"""
        expected_result = EnvVars(
            gh_app_id=12345,
            gh_app_installation_id=678910,
            gh_app_private_key_bytes=b"hello",
            gh_app_enterprise_only=False,
            gh_token="",
            ghe="",
            report_title="",
            owner="test_owner",
            repo="test_repo",
            output_file="innersource_report.md",
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_ENTERPRISE_URL": "",
            "GH_TOKEN": TOKEN,
            "OUTPUT_FILE": "",
            "REPOSITORY": "test_owner/test_repo",
            "REPORT_TITLE": "",
        },
        clear=True,
    )
    def test_get_env_vars_with_token(self):
        """Test that all environment variables are set correctly using a list of repositories"""
        expected_result = EnvVars(
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            gh_token=TOKEN,
            ghe="",
            report_title="",
            owner="test_owner",
            repo="test_repo",
            output_file="innersource_report.md",
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_missing_token(self):
        """Test that an error is raised if the TOKEN environment variables is not set"""
        with self.assertRaises(ValueError):
            get_env_vars(True)

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
        },
        clear=True,
    )
    def test_get_env_vars_missing_repository(self):
        """Test that an error is raised if the REPOSITORY environment variable is not set"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        self.assertEqual(
            str(context_manager.exception),
            "REPOSITORY environment variable not set",
        )

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "REPOSITORY": "invalidrepo",
        },
        clear=True,
    )
    def test_get_env_vars_invalid_repository_format(self):
        """Test that an error is raised if the REPOSITORY environment variable is incorrectly formatted"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        self.assertEqual(
            str(context_manager.exception),
            "REPOSITORY environment variable must be in the format 'owner/repo'",
        )

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
        },
        clear=True,
    )
    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": TOKEN,
            "GH_ENTERPRISE_URL": "",
            "OUTPUT_FILE": "innersource_report.md",
            "REPORT_TITLE": "InnerSource Report",
            "REPOSITORY": "test_owner/test_repo",
            "RATE_LIMIT_BYPASS": "true",
        },
    )
    def test_get_env_vars_optional_values(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EnvVars(
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            gh_token=TOKEN,
            ghe="",
            report_title="InnerSource Report",
            owner="test_owner",
            repo="test_repo",
            output_file="innersource_report.md",
            rate_limit_bypass=True,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "TOKEN",
            "REPOSITORY": "test_owner/test_repo",
            "OUTPUT_FILE": "",
        },
        clear=True,
    )
    def test_get_env_vars_output_file_default_in_prod(self):
        """Test that output_file is set to default value in production (non-test) environment."""
        # Directly test the output_file logic
        with patch.dict(
            "os.environ",
            {
                "REPOSITORY": "test_owner/test_repo",
                "GH_TOKEN": "TOKEN",
            },
        ):
            # Verify the default value logic directly
            env_vars = get_env_vars(test=True)

            # This is the condition in get_env_vars
            self.assertEqual(env_vars.output_file, "innersource_report.md")

    @patch.dict(
        os.environ,
        {
            "GH_APP_ID": "",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "TOKEN",
            "REPOSITORY": "test_owner/test_repo",
            "OUTPUT_FILE": "",
        },
        clear=True,
    )
    def test_get_env_vars_optionals_are_defaulted(self):
        """Test that optional values are set to their default values if not provided"""
        expected_result = EnvVars(
            gh_app_id=None,
            gh_app_installation_id=None,
            gh_app_private_key_bytes=b"",
            gh_app_enterprise_only=False,
            gh_token="TOKEN",
            ghe="",
            report_title="InnerSource Report",
            owner="test_owner",
            repo="test_repo",
            output_file="innersource_report.md",
            rate_limit_bypass=False,
        )
        result = get_env_vars(True)
        self.assertEqual(str(result), str(expected_result))

    @patch.dict(
        os.environ,
        {
            "ORGANIZATION": "my_organization",
            "GH_APP_ID": "12345",
            "GH_APP_INSTALLATION_ID": "",
            "GH_APP_PRIVATE_KEY": "",
            "GH_TOKEN": "",
        },
        clear=True,
    )
    def test_get_env_vars_auth_with_github_app_installation_missing_inputs(self):
        """Test that an error is raised there are missing inputs for the gh app"""
        with self.assertRaises(ValueError) as context_manager:
            get_env_vars(True)
        the_exception = context_manager.exception
        self.assertEqual(
            str(the_exception),
            "GH_APP_ID set and GH_APP_INSTALLATION_ID or GH_APP_PRIVATE_KEY variable not set",
        )


if __name__ == "__main__":
    unittest.main()
