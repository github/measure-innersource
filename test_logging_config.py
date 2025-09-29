"""Tests for logging_config.py"""

import io
import logging
import unittest
from unittest.mock import patch

from logging_config import get_logger, setup_logging


class TestLoggingConfig(unittest.TestCase):
    """Test cases for logging configuration"""

    def test_setup_logging_default_level(self):
        """Test that setup_logging works with default level"""
        # Clear any existing handlers first
        logger = logging.getLogger("innersource_measure_test1")
        logger.handlers.clear()
        logger = setup_logging()
        assert logger is not None
        assert logger.name == "innersource_measure"
        assert logger.level == logging.INFO

    def test_setup_logging_custom_level(self):
        """Test that setup_logging works with custom level"""
        # Use a different logger name to avoid conflicts
        logger_name = "innersource_measure_test2"
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()

        # Patch the logger creation to use our test logger
        with patch("logging_config.logging.getLogger", return_value=logger):
            test_logger = setup_logging("DEBUG")
            assert test_logger is not None
            assert test_logger.level == logging.DEBUG

    def test_get_logger(self):
        """Test that get_logger returns the configured logger"""
        # First setup logging
        setup_logging()
        logger = get_logger()
        assert logger is not None
        assert logger.name == "innersource_measure"

    def test_logging_output(self):
        """Test that logging actually produces output"""
        # Create a new logger for this test to avoid handler conflicts
        test_logger = logging.getLogger("test_output_logger")
        test_logger.handlers.clear()
        test_logger.setLevel(logging.INFO)

        # Create a string handler to capture output
        log_capture_string = io.StringIO()
        ch = logging.StreamHandler(log_capture_string)
        test_logger.addHandler(ch)

        test_logger.info("Test log message")

        log_contents = log_capture_string.getvalue()
        assert "Test log message" in log_contents

    def test_logging_prevents_duplicate_handlers(self):
        """Test that multiple calls to setup_logging don't add duplicate handlers"""
        # Use a fresh logger name
        logger_name = "innersource_measure_dup_test"
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()

        with patch("logging_config.logging.getLogger", return_value=logger):
            logger1 = setup_logging("INFO")
            handler_count_1 = len(logger1.handlers)

            logger2 = setup_logging("DEBUG")  # Second call
            handler_count_2 = len(logger2.handlers)

            # Should be the same logger with the same number of handlers
            assert logger1 is logger2
            assert handler_count_1 == handler_count_2 == 1
