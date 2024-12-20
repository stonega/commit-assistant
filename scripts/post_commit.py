#!/usr/bin/env python3

import os
import sqlite3
import subprocess
from datetime import datetime

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")


def get_commit_info():
    # Get the absolute path of the git directory and commit message file
    git_dir = subprocess.check_output(
        ["git", "rev-parse", "--absolute-git-dir"], universal_newlines=True
    ).strip()
    commit_msg_file = os.path.join(git_dir, "COMMIT_EDITMSG")

    if not os.path.exists(commit_msg_file):
        print("No commit message found. Skipping pre-commit checks.")
        exit(0)

    with open(commit_msg_file, "r") as f:
        commit_message = f.read().strip()

    return commit_message


def get_code_diff():
    """
    Get the code diff of the committed changes.
    """
    diff = subprocess.check_output(
        ["git", "diff", "--cached"], universal_newlines=True
    ).strip()
    return diff


def save_to_database(
    commit_message,
    author_name,
    author_email,
    timestamp,
    repo_url,
    repo_name,
    current_branch,
    code_diff=None,
    readme_id=None,
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
                    repo_url, repo_name, branch_name, code_diff, readme_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            readme_id,
        ),
    )

    conn.commit()
    conn.close()


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}. Please initialize it first.")
        exit(1)

    # Get commit information
    commit_message = get_commit_info()

    insert_commit_message(commit_message)
    print(f"Commit {commit_message} saved to database at {DB_PATH}")


if __name__ == "__main__":
    main()
