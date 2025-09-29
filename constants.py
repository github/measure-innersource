"""Constants used throughout the InnerSource measurement tool.

This module defines commonly used constants to avoid magic values
and improve code maintainability.
"""

# GitHub issue body character limit
GITHUB_ISSUE_BODY_MAX_CHARS = 65535

# Default chunk size for processing data in batches
DEFAULT_CHUNK_SIZE = 100

# Minimum allowed chunk size
MIN_CHUNK_SIZE = 10
