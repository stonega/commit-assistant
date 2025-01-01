import sqlite3

import os

# Set fixed path in user's home directory
DB_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "commit-assistant", "commits.db"
)


def create_db():
    # Create directory structure if it doesn't exist
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    if os.path.exists(DB_PATH):
        backup_path = DB_PATH.replace(".db", "_backup.db")
        response = input(
            f"Database already exists at {DB_PATH}. Backup and create new? (y/N): "
        )

        if response.lower() == "y":
            os.rename(DB_PATH, backup_path)
            print(f"Existing database backed up to: {backup_path}")
        else:
            raise SystemExit("Database creation cancelled by user.")
        print(f"Existing database backed up to: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the commits table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        author_name TEXT NOT NULL,
        author_email TEXT NOT NULL,
        commit_message TEXT NOT NULL,
        repo_url TEXT NOT NULL,
        repo_name TEXT NOT NULL,
        branch_name TEXT NOT NULL,
        code_diff TEXT,
        added_lines INTEGER DEFAULT 0,
        removed_lines INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
    print("Database and tables created!")
