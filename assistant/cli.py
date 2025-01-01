import sys

from .analyze import summarize_week_commit
from .cli_args import parse_args
from .cli_interface import CLIInterface
from .hooks_setup import setup_global_hooks
from .husky_hooks_setup import setup_husky_hooks
from .post_commit import save_commit_message
from .pre_commit import save_commit_diff
from .prepare_commit_msg import prepare_commit_msg
from .setup_db import create_db
from .config import config


class Assistant:
    COMMAND_HELP = {
        "run": "Start the interactive assistant",
        "setup": """Initial setup of the assistant:
    - Configure Gemini API key
    - Initialize database
    - Setup git hooks""",
        "commit": "Create a new commit with AI assistance",
        "pre-commit": "Run pre-commit hook to save commit diff",
        "post-commit": "Run post-commit hook to save commit message",
        "setup-husky": "Configure Husky git hooks for the project",
        "summary": "Generate a summary of recent commits",
    }

    def __init__(self):
        self.cli_interface = CLIInterface()

    def show_help(self):
        """Display detailed help for all commands"""
        help_text = ["\nCommit Assistant Commands", "=" * 50]

        # Add command descriptions
        for cmd, desc in self.COMMAND_HELP.items():
            help_text.extend([f"\n{cmd}", "-" * len(cmd), desc])

        # Add examples
        help_text.extend(
            [
                "\nExamples:",
                "-" * 8,
                "coas setup         # Run initial setup",
                "coas commit        # Create a new commit",
                "coas setup-husky   # Setup Husky git hooks",
                "coas summary       # View commit summary",
            ]
        )

        self.cli_interface.display_info("\n".join(help_text))

    def setup(self):
        """Run initial setup"""
        # 0. Config
        config.get("gemini", "api_key")

        # 1. Init db
        create_db()
        # 2. Setup git hooks
        setup_global_hooks()

    def commit(self):
        prepare_commit_msg()

    def pre_commit(self):
        save_commit_diff()

    def post_commit(self):
        save_commit_message()

    def setup_husky(self):
        setup_husky_hooks()

    def summary(self):
        summarize_week_commit()


def cli():
    # Create and run assistant
    try:
        args = parse_args()
        assistant = Assistant()

        if hasattr(args, "--help-command") and args.help:
            assistant.show_help()
            return

        if args.command == "setup":
            assistant.setup()
        elif args.command == "commit":
            assistant.commit()
        elif args.command == "pre-commit":
            assistant.pre_commit()
        elif args.command == "post-commit":
            assistant.post_commit()
        elif args.command == "setup-husky":
            assistant.setup_husky()
        elif args.command == "summary":
            assistant.summary()

    except Exception as e:
        # Other runtime errors
        CLIInterface.display_error(str(e))
        sys.exit(1)
