"""Markdown file processing utilities for the InnerSource measurement tool.

This module provides helper functions for working with markdown files, particularly
for handling large files that may exceed GitHub's character limits for issue bodies.

GitHub issues have a maximum character limit of 65,535 characters for the body content.
When InnerSource reports are large, they need to be split into smaller files that can
fit within this limit.

Functions:
    markdown_too_large_for_issue_body: Check if a markdown file is too large for GitHub issues
    split_markdown_file: Split large markdown files into smaller, manageable chunks

Common Use Cases:
    - Splitting large InnerSource reports for GitHub issue compatibility
    - Managing file sizes for various markdown-based systems with character limits
    - Preparing reports for different output formats with size constraints
"""


def markdown_too_large_for_issue_body(file_path: str, max_char_count: int) -> bool:
    """
    Check if a markdown file exceeds GitHub's issue body character limit.

    GitHub issues have a maximum character limit for the body content. This function
    reads a markdown file and determines if it would exceed this limit.

    Args:
        file_path (str): The path to the markdown file to check. Must be a valid
                        file path that exists and is readable.
        max_char_count (int): The maximum number of characters allowed in a GitHub
                             issue body. For GitHub.com, this is typically 65,535.

    Returns:
        bool: True if the file contents exceed the character limit, False otherwise.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read due to permission issues.
        UnicodeDecodeError: If the file contains invalid UTF-8 encoding.

    Examples:
        >>> # Check if a report is too large for GitHub issues
        >>> is_too_large = markdown_too_large_for_issue_body("report.md", 65535)
        >>> if is_too_large:
        ...     print("File needs to be split for GitHub issues")
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        return len(file_contents) > max_char_count


def split_markdown_file(file_path: str, max_char_count: int) -> None:
    """
    Split a large markdown file into smaller files that fit within size limits.

    This function reads a markdown file and splits it into multiple smaller files
    when the original file is too large for GitHub issues or other systems with
    character limits.

    Args:
        file_path (str): The path to the markdown file to split. The file must exist
                        and be readable. The function will create new files with
                        numbered suffixes in the same directory.
        max_char_count (int): The maximum number of characters allowed in each split
                             file. Content will be split at this boundary.

    Returns:
        None: This function performs file operations and creates new split files.

    Side Effects:
        - Creates new files with names like "{original_name}_0.md", "{original_name}_1.md", etc.
        - Each new file contains a portion of the original content
        - Files are created in the same directory as the original file
        - The original file is not modified or deleted

    File Naming:
        - Original file: "report.md"
        - Split files: "report_0.md", "report_1.md", "report_2.md", etc.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read or new files cannot be created.
        UnicodeDecodeError: If the file contains invalid UTF-8 encoding.

    Examples:
        >>> # Split a large report into smaller files
        >>> split_markdown_file("large_report.md", 65535)
        >>> # This creates: large_report_0.md, large_report_1.md, etc.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_contents = file.read()
        contents_list = [
            file_contents[i : i + max_char_count]
            for i in range(0, len(file_contents), max_char_count)
        ]
        for i, content in enumerate(contents_list):
            with open(f"{file_path[:-3]}_{i}.md", "w", encoding="utf-8") as new_file:
                new_file.write(content)
