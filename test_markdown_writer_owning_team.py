"""Unit tests for markdown_writer with owning_team override."""

from unittest.mock import MagicMock

from markdown_writer import write_to_markdown


def test_write_to_markdown_with_owning_team_override(tmp_path):
    """Test markdown output when owning team is explicitly specified."""
    output_file = tmp_path / "test_owning_team.md"

    # Mock repository object
    mock_repo = MagicMock()
    mock_repo.full_name = "org/repo"

    # Call with None for original_commit_author and manager (simulating owning_team override)
    write_to_markdown(
        report_title="Test Report with Owning Team",
        output_file=str(output_file),
        innersource_ratio=0.35,
        repo_data=mock_repo,
        original_commit_author=None,
        original_commit_author_manager=None,
        team_members_that_own_the_repo=["alice", "bob", "charlie"],
        all_contributors=["alice", "bob", "charlie", "dave", "eve"],
        innersource_contributors=["dave", "eve"],
        innersource_contribution_counts={"dave": 15, "eve": 8},
        team_member_contribution_counts={"alice": 25, "bob": 12, "charlie": 5},
    )

    # Verify the file was created
    assert output_file.exists()

    # Read the content
    content = output_file.read_text(encoding="utf-8")

    # Verify the content includes the expected sections
    assert "# Test Report with Owning Team" in content
    assert "## Repository: org/repo" in content
    assert "### InnerSource Ratio: 35.00%" in content
    assert "### Team ownership is explicitly specified" in content
    # Should NOT contain original commit author and manager
    assert "Original Commit Author:" not in content
    assert "Manager:" not in content
    # Should contain team members
    assert "## Team Members that Own the Repo:" in content
    assert "- alice" in content
    assert "- bob" in content
    assert "- charlie" in content


def test_write_to_markdown_with_original_author(tmp_path):
    """Test markdown output when team is determined by algorithm."""
    output_file = tmp_path / "test_algorithm.md"

    # Mock repository object
    mock_repo = MagicMock()
    mock_repo.full_name = "org/repo"

    # Call with original_commit_author and manager (normal algorithm mode)
    write_to_markdown(
        report_title="Test Report with Algorithm",
        output_file=str(output_file),
        innersource_ratio=0.35,
        repo_data=mock_repo,
        original_commit_author="alice",
        original_commit_author_manager="manager1",
        team_members_that_own_the_repo=["alice", "bob", "charlie"],
        all_contributors=["alice", "bob", "charlie", "dave", "eve"],
        innersource_contributors=["dave", "eve"],
        innersource_contribution_counts={"dave": 15, "eve": 8},
        team_member_contribution_counts={"alice": 25, "bob": 12, "charlie": 5},
    )

    # Verify the file was created
    assert output_file.exists()

    # Read the content
    content = output_file.read_text(encoding="utf-8")

    # Verify the content includes the expected sections
    assert "# Test Report with Algorithm" in content
    assert "## Repository: org/repo" in content
    assert "### InnerSource Ratio: 35.00%" in content
    assert "### Original Commit Author: alice (Manager: manager1)" in content
    # Should NOT contain the override message
    assert "Team ownership is explicitly specified" not in content
