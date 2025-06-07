"""
A module for writing an InnerSource Report to a markdown file.
"""


def write_to_markdown(
    report_title="",
    output_file="",
) -> None:
    """
    Write an InnerSource Report to a markdown file.
    Args:
        report_title (str): The title of the report.
        output_file (str): The name of the output markdown file.

    Returns:
        None
    """
    output_file_name = output_file if output_file else "innersource_report.md"
    with open(output_file_name, "w", encoding="utf-8") as file:
        file.write(f"# {report_title}\n\n")

        file.write("no op\n\n")
