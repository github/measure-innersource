"""Tests for constants.py"""

import unittest

from constants import DEFAULT_CHUNK_SIZE, GITHUB_ISSUE_BODY_MAX_CHARS, MIN_CHUNK_SIZE


class TestConstants(unittest.TestCase):
    """Test cases for constants"""

    def test_github_issue_body_max_chars(self):
        """Test that the GitHub issue body limit constant is correct"""
        assert GITHUB_ISSUE_BODY_MAX_CHARS == 65535

    def test_default_chunk_size(self):
        """Test that the default chunk size constant is correct"""
        assert DEFAULT_CHUNK_SIZE == 100

    def test_min_chunk_size(self):
        """Test that the minimum chunk size constant is correct"""
        assert MIN_CHUNK_SIZE == 10

    def test_constants_are_integers(self):
        """Test that all constants are integers"""
        assert isinstance(GITHUB_ISSUE_BODY_MAX_CHARS, int)
        assert isinstance(DEFAULT_CHUNK_SIZE, int)
        assert isinstance(MIN_CHUNK_SIZE, int)

    def test_chunk_size_relationships(self):
        """Test that chunk size constants have correct relationships"""
        assert MIN_CHUNK_SIZE <= DEFAULT_CHUNK_SIZE
        assert MIN_CHUNK_SIZE > 0
        assert DEFAULT_CHUNK_SIZE > 0
