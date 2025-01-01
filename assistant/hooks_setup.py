import os
import stat
from pathlib import Path
import subprocess


def get_git_global_config_dir():
    """Get the Git global config directory"""
    try:
        config_dir = subprocess.check_output(
            ["git", "config", "--global", "core.hooksPath"],
            stderr=subprocess.PIPE,
            universal_newlines=True,
        ).strip()
        if config_dir:
            return Path(config_dir)
    except subprocess.CalledProcessError:
        pass

    # Default to ~/.git/hooks if not set
    return Path.home() / ".git" / "hooks"


def create_hook_script(hook_path: Path, content: str):
    """Create a hook script with the given content"""
    hook_path.parent.mkdir(parents=True, exist_ok=True)

    with open(hook_path, "w") as f:
        f.write("#!/bin/sh\n")
        f.write(content)

    # Make the hook executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)


def setup_pre_commit_hook():
    """Set up the global pre-commit hook"""
    hooks_dir = get_git_global_config_dir()
    pre_commit_path = hooks_dir / "pre-commit"

    pre_commit_content = """
# Pre-commit hook
echo "Running pre-commit hook..."
coas pre-commit
"""
    create_hook_script(pre_commit_path, pre_commit_content)
    print(f"Pre-commit hook installed at: {pre_commit_path}")


def setup_post_commit_hook():
    """Set up the global post-commit hook"""
    hooks_dir = get_git_global_config_dir()
    post_commit_path = hooks_dir / "post-commit"

    post_commit_content = """
# Post-commit hook
echo "Running post-commit hook..."
coas post-commit
"""
    create_hook_script(post_commit_path, post_commit_content)
    print(f"Post-commit hook installed at: {post_commit_path}")


def setup_global_hooks():
    """Set up all global Git hooks"""
    hooks_dir = get_git_global_config_dir()

    # Configure Git to use global hooks
    subprocess.run(["git", "config", "--global", "core.hooksPath", str(hooks_dir)])

    setup_pre_commit_hook()
    setup_post_commit_hook()

    print(f"\nGlobal hooks directory configured at: {hooks_dir}")
    print("Git hooks setup complete!")
