import argparse

from rich.console import Console

console = Console()


def color_text(text: str, rgb: tuple, bold: bool = False):
    """prints a colored text in the terminal using ANSI escape codes based on the rgb values

    Args:
        text (str): the text to be printed
        rgb (tuple): the rgb values of the color
    """
    if bold:
        return f"\033[1m\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[m"
    else:
        return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[m"


def make_title(title):
    return color_text(title, rgb=(128, 128, 0), bold=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description=color_text(
            "SheetFusion: A tool for merging cover sheets with exams",
            rgb=(76, 122, 164),
            bold=True,
        ),
        add_help=False,
    )

    def formatter(prog):
        return argparse.HelpFormatter(prog, width=100, max_help_position=64)

    parser.formatter_class = formatter

    ############################################################
    # Help options
    help_options = parser.add_argument_group(make_title("Help options"))
    help_options.add_argument(
        "--help",
        "-h",
        help="Show this help message and exit",
        action="help",
    )
    ############################################################

    ############################################################
    # Required arguments
    required_args = parser.add_argument_group(make_title("Required arguments"))
    required_args.add_argument(
        "--cover-sheets",
        "-c",
        dest="cover_sheets_file",
        help="The PDF file containing the cover sheets",
        required=True,
        metavar="",
    )
    required_args.add_argument(
        "--exam",
        "-e",
        help="The PDF file containing the exam",
        required=True,
        dest="exam_file",
        metavar="",
    )
    ############################################################

    ############################################################
    # Optional arguments
    optional_args = parser.add_argument_group(make_title("Optional arguments"))
    optional_args.add_argument(
        "--output-dir",
        "-o",
        help="The directory to output the merged PDFs to",
        default=".",
        metavar="",
    )
    optional_args.add_argument(
        "--overwrite",
        help="Overwrite existing files",
        action="store_true",
        dest="overwrite",
    )
    ############################################################

    parsed_args = parser.parse_args()

    return parsed_args
