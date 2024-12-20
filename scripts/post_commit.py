#!/usr/bin/env python3
import os
import sqlite3
import subprocess


DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")
# Configure Gemini API

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


def insert_commit_message(commit_message):
    """
    Update the latest record in the commits table with the commit message.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update the most recent record (highest ID) with the commit message
    cursor.execute(
        """
        UPDATE commits 
        SET commit_message = ?
        WHERE id = (SELECT MAX(id) FROM commits)
        """,
        (commit_message,),
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
