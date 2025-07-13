"""
Tests for config.py specifically for the chunk_size parameter
"""

from config import get_env_vars


class TestChunkSize:
    """
    Test cases for the chunk_size parameter in config.py
    """

    def test_get_env_vars_with_default_chunk_size(self, monkeypatch):
        """
        Test that chunk_size is set to default (100) when not specified
        """
        monkeypatch.setenv("REPOSITORY", "owner/repo")
        monkeypatch.setenv("GH_TOKEN", "token")

        env_vars = get_env_vars(test=True)
        assert env_vars.chunk_size == 100

    def test_get_env_vars_with_custom_chunk_size(self, monkeypatch):
        """
        Test that chunk_size is set to the custom value when specified
        """
        monkeypatch.setenv("REPOSITORY", "owner/repo")
        monkeypatch.setenv("GH_TOKEN", "token")
        monkeypatch.setenv("CHUNK_SIZE", "200")

        env_vars = get_env_vars(test=True)
        assert env_vars.chunk_size == 200

    def test_get_env_vars_with_small_chunk_size(self, monkeypatch):
        """
        Test that chunk_size is set to minimum 10 when specified value is too small
        """
        monkeypatch.setenv("REPOSITORY", "owner/repo")
        monkeypatch.setenv("GH_TOKEN", "token")
        monkeypatch.setenv("CHUNK_SIZE", "5")

        env_vars = get_env_vars(test=True)
        assert env_vars.chunk_size == 10

    def test_get_env_vars_with_invalid_chunk_size(self, monkeypatch):
        """
        Test that chunk_size is set to default (100) when an invalid value is specified
        """
        monkeypatch.setenv("REPOSITORY", "owner/repo")
        monkeypatch.setenv("GH_TOKEN", "token")
        monkeypatch.setenv("CHUNK_SIZE", "not_a_number")

        env_vars = get_env_vars(test=True)
        assert env_vars.chunk_size == 100
