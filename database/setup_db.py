import sqlite3
import os

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")


def create_db():
    # Backup existing database if it exists
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH.replace(".db", "_backup.db")
        os.rename(DB_PATH, backup_path)
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


if __name__ == "__main__":
    create_db()
