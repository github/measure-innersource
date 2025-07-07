"""Unit tests for measure_innersource.evaluate_markdown_file_size."""

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
