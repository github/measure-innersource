"""Logging configuration and utilities for the InnerSource measurement tool.

This module provides centralized logging configuration to replace
print statements with proper logging levels.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure and return a logger for the InnerSource measurement tool.

    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                    Defaults to INFO.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("innersource_measure")

    # Avoid adding multiple handlers if logger is already configured
    if logger.handlers:
        return logger

    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger() -> logging.Logger:
    """Get the configured logger instance.

    Returns:
        logging.Logger: The configured logger for the application
    """
    return logging.getLogger("innersource_measure")
