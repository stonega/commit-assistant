import argparse
from .__version__ import VERSION
from .cli_interface import WELCOME_MESSAGE


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments for configuration."""
    parser = argparse.ArgumentParser(
        description="=" * 58 + "\n" + WELCOME_MESSAGE + "\n" + "=" * 58,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-v", "--version", action="version", version=VERSION)
    parser.add_argument(
        "--help-command",
        action="store_true",
        help="Show detailed help information for all commands",
    )
    parser.add_argument(
        "command",
        nargs="?",  # Make command optional when showing help
        choices=[
            "setup",
            "pre-commit",
            "post-commit",
            "setup-husky",
            "summary",
            "commit",
        ],
        help="Command to execute",
    )

    return parser.parse_args()
