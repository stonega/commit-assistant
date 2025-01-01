import sys
from pathlib import Path


class HuskyNotInstalledError(Exception):
    """Raised when Husky is not installed in the project"""

    pass


def get_husky_config_dir():
    """Get husky config directory"""
    husky_dir = Path(".husky")
    husky_config_dir = husky_dir / "_"

    if not husky_dir.exists():
        raise HuskyNotInstalledError(
            "Husky is not installed. Please install husky first: "
            "npx husky-init && npm install"
        )

    if not husky_config_dir.exists():
        raise HuskyNotInstalledError(
            "Husky configuration directory is missing. "
            "Please reinstall husky: npx husky-init && npm install"
        )

    return husky_config_dir


def setup_pre_commit_hook():
    """Set up the global pre-commit hook"""
    hooks_dir = get_husky_config_dir()
    pre_commit_path = hooks_dir / "pre-commit"

    pre_commit_content = """
# Pre-commit hook
echo "Running pre-commit hook..."
coas pre-commit
"""

    if pre_commit_path.exists():
        # Read existing content
        lines = pre_commit_path.read_text().splitlines()

        # Combine first line with new content and remaining lines
        new_content = lines[0] + "\n" + pre_commit_content
        if len(lines) > 1:
            new_content += "\n".join(lines[1:])

        # Write back to file
        pre_commit_path.write_text(new_content)

        print(f"Pre-commit hook updated at: {pre_commit_path}")
    else:
        print(f"Error: Pre-commit hook file not found at: {pre_commit_path}")
        sys.exit(1)
    print(f"Pre-commit hook installed at: {pre_commit_path}")


def setup_post_commit_hook():
    """Set up the global post-commit hook"""
    hooks_dir = get_husky_config_dir()
    post_commit_path = hooks_dir / "post-commit"

    post_commit_content = """
# Post-commit hook
echo "Running post-commit hook..."
coas post-commit
"""

    if post_commit_path.exists():
        # Read existing content
        lines = post_commit_path.read_text().splitlines()

        # Combine first line with new content and remaining lines
        new_content = lines[0] + "\n" + post_commit_content
        if len(lines) > 1:
            new_content += "\n".join(lines[1:])

        # Write back to file
        post_commit_path.write_text(new_content)

        print(f"Post-commit hook updated at: {post_commit_path}")
    else:
        print(f"Error: Post-commit hook file not found at: {post_commit_path}")
        sys.exit(1)


def setup_husky_hooks():
    """Set up all Git hooks"""
    try:
        hooks_dir = get_husky_config_dir()

        setup_pre_commit_hook()
        setup_post_commit_hook()

        print(f"\nHooks directory configured at: {hooks_dir}")
        print("Git hooks setup complete!")

    except HuskyNotInstalledError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error setting up hooks: {str(e)}", file=sys.stderr)
        sys.exit(1)
