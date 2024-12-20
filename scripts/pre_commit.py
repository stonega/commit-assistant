#!/usr/bin/env python3

import os
import sqlite3
import subprocess
from datetime import datetime

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")


def get_commit_info():
    """
    Get commit message, author name, and email from the current commit being made.
    """
    # Get the commit message from the COMMIT_EDITMSG file
    git_dir = subprocess.check_output(
        ["git", "rev-parse", "--git-dir"], universal_newlines=True
    ).strip()
    commit_msg_file = os.path.join(git_dir, "COMMIT_EDITMSG")

    if not os.path.exists(commit_msg_file):
        print("No commit message found. Skipping pre-commit checks.")
        exit(0)

    with open(commit_msg_file, "r") as f:
        commit_message = f.read().strip()

    # Get the author information from git config
    author_name = subprocess.check_output(
        ["git", "config", "user.name"], universal_newlines=True
    ).strip()
    author_email = subprocess.check_output(
        ["git", "config", "user.email"], universal_newlines=True
    ).strip()
    timestamp = datetime.now().timestamp()

    return commit_message, author_name, author_email, timestamp


def get_code_diff():
    """
    Get the code diff of the committed changes.
    """
    diff = subprocess.check_output(
        ["git", "diff", "--cached"], universal_newlines=True
    ).strip()
    return diff


def save_readme_to_database():
    """
    Check for a README file and save its content to the database.
    Returns the ID of the saved README, or None if no README exists.
    """
    readme_filenames = ["README.md", "README.txt"]

    if not DB_PATH:
        raise ValueError("COMMIT_DB_PATH environment variable is not set")

    for filename in readme_filenames:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                readme_content = file.read()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            timestamp = datetime.now().timestamp()

            # Insert the README content into the project_readme table
            cursor.execute(
                """
            INSERT INTO project_readme (readme_content, timestamp)
            VALUES (?, ?)
            """,
                (readme_content, timestamp),
            )

            conn.commit()

            # Get the ID of the newly inserted README
            readme_id = cursor.lastrowid

            conn.close()
            print(
                f"README file '{filename}' saved to the database with ID {readme_id}."
            )
            return readme_id

    print("No README file found. Skipping saving README to the database.")
    return None


def save_to_database(
    commit_message, author_name, author_email, timestamp, code_diff=None, readme_id=None
):
    """
    Save the commit information and code diff to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert the commit information
    cursor.execute(
        """
    INSERT INTO commits (timestamp, author_name, author_email, commit_message, code_diff, readme_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        (timestamp, author_name, author_email, commit_message, code_diff, readme_id),
    )

    conn.commit()
    conn.close()


def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}. Please initialize it first.")
        exit(1)

    # Get commit information
    commit_message, author_name, author_email, timestamp = get_commit_info()

    # If the commit message is not 'initial commit', capture the code diff
    code_diff = None
    if commit_message.lower() != "initial commit":
        code_diff = get_code_diff()

    # Save README file to the database and get its ID
    readme_id = save_readme_to_database()

    # Save commit info and code diff to the database
    save_to_database(
        commit_message, author_name, author_email, timestamp, code_diff, readme_id
    )

    print(f"Commit information and README (if exists) saved to {DB_PATH}")


if __name__ == "__main__":
    main()
