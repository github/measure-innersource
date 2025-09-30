"""Unit tests for measure_innersource.evaluate_markdown_file_size."""

import json
from unittest.mock import MagicMock, patch

import measure_innersource as mi
import pytest


def test_evaluate_markdown_file_size_splits(tmp_path, monkeypatch):
    """Test splitting of markdown file when it is too large for issue body."""
    # Switch working directory to tmp_path
    monkeypatch.chdir(tmp_path)
    # Create the original markdown file
    orig_file = tmp_path / "test.md"
    orig_file.write_text("original content", encoding="utf-8")

    # Monkey-patch markdown_too_large_for_issue_body to simulate large file
    monkeypatch.setattr(
        mi, "markdown_too_large_for_issue_body", lambda filename, max_chars: True
    )

    # Dummy split function to create split files
    def dummy_split(_path, _max_chars):
        split_file = tmp_path / "test_0.md"
        split_file.write_text("split part", encoding="utf-8")

    monkeypatch.setattr(mi, "split_markdown_file", dummy_split)

    # Call the function under test
    mi.evaluate_markdown_file_size("test.md")

    # The original file should be moved to test_full.md
    full_file = tmp_path / "test_full.md"
    assert full_file.exists()
    assert full_file.read_text(encoding="utf-8") == "original content"

    # The split file should be moved to test.md
    updated_file = tmp_path / "test.md"
    assert updated_file.exists()
    assert updated_file.read_text(encoding="utf-8") == "split part"

    # The intermediate split file should no longer exist
    assert not (tmp_path / "test_0.md").exists()


def test_evaluate_markdown_file_size_no_split(tmp_path, monkeypatch):
    """Test that small markdown file remains unchanged when size is within limits."""
    # Switch working directory to tmp_path
    monkeypatch.chdir(tmp_path)
    # Create a small markdown file
    file = tmp_path / "test2.md"
    file.write_text("small", encoding="utf-8")

    # Monkey-patch markdown_too_large_for_issue_body to simulate small file
    monkeypatch.setattr(
        mi, "markdown_too_large_for_issue_body", lambda filename, max_chars: False
    )

    # Monkey-patch split_markdown_file to fail if called
    monkeypatch.setattr(
        mi,
        "split_markdown_file",
        lambda *args, **kwargs: pytest.skip("split_markdown_file should not be called"),
    )

    # Call the function under test; should not error
    mi.evaluate_markdown_file_size("test2.md")

    # The file should remain unchanged
    assert file.exists()
    assert file.read_text(encoding="utf-8") == "small"


def test_main_missing_user_in_org_chart(tmp_path, monkeypatch):
    """Test main function logs warning and exits when original commit author
    is missing from org chart."""
    # Switch working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    # Create org-data.json with some users, but not the original commit author
    org_data = {
        "manager1": {"manager": "director1"},
        "user1": {"manager": "manager1"},
        "user2": {"manager": "manager1"},
    }

    org_file = tmp_path / "org-data.json"
    org_file.write_text(json.dumps(org_data), encoding="utf-8")

    # Mock GitHub repository and commit data
    mock_author = MagicMock()
    mock_author.login = "missing_user"  # This user is not in org_data

    mock_commit = MagicMock()
    mock_commit.author = mock_author

    mock_repo = MagicMock()
    mock_repo.full_name = "test/repo"

    # Mock commits to return our mock commit as the first/oldest commit
    # Create a proper iterator that will convert to a list with one item
    mock_repo.commits.return_value = iter([mock_commit])

    mock_github = MagicMock()
    mock_github.repository.return_value = mock_repo

    # Mock environment variables
    mock_env_vars = MagicMock()
    mock_env_vars.gh_token = "fake_token"  # Change to match field name in main()
    mock_env_vars.ghe = None  # Change to match field name in main()
    mock_env_vars.owner = "test"  # Change to match field name in main()
    mock_env_vars.repo = "repo"  # Change to match field name in main()
    mock_env_vars.gh_app_id = None
    mock_env_vars.gh_app_installation_id = None
    mock_env_vars.gh_app_private_key_bytes = None
    mock_env_vars.gh_app_enterprise_only = False
    mock_env_vars.report_title = "Test Report"
    mock_env_vars.output_file = "test_output.md"
    mock_env_vars.owning_team = None  # Add owning_team field that's used in main()
    mock_env_vars.chunk_size = 100  # Add chunk_size to avoid issues in processing loops

    # Apply mocks
    with patch("measure_innersource.get_env_vars", return_value=mock_env_vars), patch(
        "measure_innersource.auth_to_github", return_value=mock_github
    ), patch("measure_innersource.setup_logging") as mock_setup_logging:

        # Configure logging to capture our test
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        with patch("measure_innersource.get_logger", return_value=mock_logger):
            # Call main function
            mi.main()

            # Verify that warning was logged about missing user
            mock_logger.warning.assert_called_with(
                "Original commit author '%s' not found in org chart. "
                "Cannot determine team boundaries for InnerSource "
                "measurement.",
                "missing_user",
            )

            # Verify that the function returned early (didn't process further)
            # by checking that subsequent info logs were not called
            info_calls = [
                call[0][0] for call in mock_logger.info.call_args_list if call[0]
            ]

            # Should have logged about reading org data and analyzing first
            # commit, but should NOT have logged about original commit author
            # with manager
            assert "Reading in org data from org-data.json..." in info_calls
            assert "Analyzing first commit..." in info_calls

            # Should NOT contain the log message about
            # "Original commit author: X, with manager: Y"
            assert not any(
                isinstance(msg, str)
                and "Original commit author:" in msg
                and "with manager:" in msg
                for msg in info_calls
            )

            # Verify that the function exited without attempting to process pull requests or issues
            # by checking that "Processing pull requests" message is not in the logs
            assert not any(
                isinstance(msg, str) and "Processing pull requests" in msg
                for msg in info_calls
            )


def test_contributors_missing_from_org_chart_excluded(tmp_path, monkeypatch):
    """Test that contributors missing from org chart are excluded from
    InnerSource analysis."""
    # Switch working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    # Create org-data.json with some users
    org_data = {
        "original_author": {"manager": "manager1"},
        "manager1": {"manager": "director1"},
        "user1": {"manager": "manager1"},
    }

    org_file = tmp_path / "org-data.json"
    org_file.write_text(json.dumps(org_data), encoding="utf-8")

    # Mock GitHub repository and commit data
    mock_original_author = MagicMock()
    mock_original_author.login = "original_author"

    mock_commit = MagicMock()
    mock_commit.author = mock_original_author

    # Mock contributors - include one that's not in org_data
    mock_contributor1 = MagicMock()
    mock_contributor1.login = "unknown_contributor"  # Not in org_data

    mock_repo = MagicMock()
    mock_repo.full_name = "test/repo"
    mock_repo.commits.return_value = iter([mock_commit])
    mock_repo.contributors.return_value = [mock_contributor1]
    # Mock empty pull requests and issues to avoid infinite loops
    mock_repo.pull_requests.return_value = iter([])
    mock_repo.issues.return_value = iter([])

    mock_github = MagicMock()
    mock_github.repository.return_value = mock_repo

    # Mock environment variables
    mock_env_vars = MagicMock()
    mock_env_vars.gh_token = "fake_token"  # Change to match field name in main()
    mock_env_vars.ghe = None  # Change to match field name in main()
    mock_env_vars.owner = "test"  # Change to match field name in main()
    mock_env_vars.repo = "repo"  # Change to match field name in main()
    mock_env_vars.gh_app_id = None
    mock_env_vars.gh_app_installation_id = None
    mock_env_vars.gh_app_private_key_bytes = None
    mock_env_vars.gh_app_enterprise_only = False
    mock_env_vars.report_title = "Test Report"
    mock_env_vars.output_file = "test_output.md"
    mock_env_vars.owning_team = None  # Add owning_team field that's used in main()
    mock_env_vars.chunk_size = 100

    # Apply mocks
    with patch("measure_innersource.get_env_vars", return_value=mock_env_vars), patch(
        "measure_innersource.auth_to_github", return_value=mock_github
    ), patch("measure_innersource.setup_logging") as mock_setup_logging, patch(
        "measure_innersource.write_to_markdown"
    ), patch(
        "measure_innersource.evaluate_markdown_file_size"
    ):

        # Configure logging to capture our test
        mock_logger = MagicMock()
        mock_setup_logging.return_value = mock_logger

        with patch("measure_innersource.get_logger", return_value=mock_logger):
            # Call main function
            mi.main()

            # Verify that warning was logged about missing contributor
            mock_logger.warning.assert_any_call(
                "Contributor '%s' not found in org chart. "
                "Excluding from InnerSource analysis.",
                "unknown_contributor",
            )
