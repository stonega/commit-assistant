#!/usr/bin/env python3

import os
import sqlite3
import subprocess
from datetime import datetime

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")


def get_commit_info():
    """
    Get commit message, author name, email, and repository information from the current commit being made.
    """

    # Get the author information from git config
    author_name = subprocess.check_output(
        ["git", "config", "user.name"], universal_newlines=True
    ).strip()
    author_email = subprocess.check_output(
        ["git", "config", "user.email"], universal_newlines=True
    ).strip()

    # Get repository information
    repo_url = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"], universal_newlines=True
    ).strip()

    # Extract org/username and repo name from URL
    if ":" in repo_url:  # SSH format: git@github.com:org/repo.git
        path_part = repo_url.split(":")[-1]
    else:  # HTTPS format: https://github.com/org/repo.git
        path_part = repo_url.split("//")[-1].split("/", 1)[-1]

    # Remove .git and split into org/repo
    path_parts = path_part.replace(".git", "").split("/")
    if len(path_parts) >= 2:
        org_or_user = path_parts[-2]
        repo_name = f"{org_or_user}/{path_parts[-1]}"
    else:
        repo_name = path_parts[-1]

    current_branch = subprocess.check_output(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], universal_newlines=True
    ).strip()

    timestamp = datetime.now().timestamp()

    return (
        author_name,
        author_email,
        timestamp,
        repo_url,
        repo_name,
        current_branch,
    )


def get_code_diff():
    """
    Get the code diff of the committed changes, limited to 1000 lines.
    Returns tuple of (diff_content, total_lines, added_lines, removed_lines)
    """
    diff = subprocess.check_output(
        ["git", "diff", "--cached"], universal_newlines=True
    ).strip()

    # Calculate added and removed lines
    added_lines = 0
    removed_lines = 0
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added_lines += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines += 1

    # Split into lines and limit to 1000 lines
    diff_lines = diff.splitlines()[:1000]

    if len(diff_lines) == 1000:
        diff_lines.append("\n... (diff truncated at 1000 lines)")

    return ("\n".join(diff_lines), added_lines, removed_lines)


def save_to_database(
    commit_message,
    author_name,
    author_email,
    timestamp,
    repo_url,
    repo_name,
    current_branch,
    code_diff=None,
    added_lines=0,
    removed_lines=0,
):
    """
    Save the commit information and code diff to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert the commit information
    cursor.execute(
        """
                INSERT INTO commits (
                    timestamp, author_name, author_email, commit_message, 
                    repo_url, repo_name, branch_name, code_diff, added_lines, removed_lines
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
        (
            timestamp,
            author_name,
            author_email,
            commit_message,
            repo_url,
            repo_name,
            current_branch,
            code_diff,
            added_lines,
            removed_lines,
        ),
    )

    conn.commit()
    conn.close()


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}. Please initialize it first.")
        exit(1)

    # If the commit message is not 'initial commit', capture the code diff
    code_diff = None
    # Get commit information
    (
        author_name,
        author_email,
        timestamp,
        repo_url,
        repo_name,
        current_branch,
    ) = get_commit_info()

    (code_diff, added_lines, removed_lines) = get_code_diff()
    print("Code diff captured.")

    # Save commit info and code diff to the database
    save_to_database(
        "",
        author_name,
        author_email,
        timestamp,
        repo_url,
        repo_name,
        current_branch,
        code_diff,
        added_lines,
        removed_lines,
    )

    print(f"Commit saved to database at {DB_PATH}")


if __name__ == "__main__":
    main()
