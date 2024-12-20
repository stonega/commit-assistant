import sqlite3
from datetime import datetime, timedelta
<<<<<<< HEAD
from openai import OpenAI
import os

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")
=======
import google.generativeai as genai
import os

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")
# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
>>>>>>> Snippet


# Step 1: Get commits for the current week
def get_commits_for_current_week(db_path):
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = today.replace(hour=23, minute=59, second=59, microsecond=999999)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Convert datetime objects to Unix timestamps for SQLite comparison
    start_timestamp = start_of_week.timestamp()
    end_timestamp = end_of_week.timestamp()

    print(f"Fetching commits between {start_of_week} and {end_of_week}")

    cursor.execute(
        """
        SELECT datetime(timestamp, 'unixepoch'), author_name, commit_message
        FROM commits
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    """,
        (start_timestamp, end_timestamp),
    )

    commits = cursor.fetchall()
    conn.close()
    return commits


# Step 2: Format commits for OpenAI
def format_commits(commits):
    if not commits:
        return "No commits were made this week."

    formatted = ["Commits for the current week:\n"]
    for timestamp, author, message in commits:
        formatted.append(f"- [{timestamp}] {author}: {message}")
    return "\n".join(formatted)


# Step 3: Summarize commits using Gemini
def summarize_commits_with_gemini(commit_summary):
    if not commit_summary:
        return "No commits were made this week."

    # Create Gemini model instance
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    Below is the list of Git commits made this week. Summarize the work done during the week in a concise and professional manner:
    
    {commit_summary}
    """

    # Generate response
    response = model.generate_content(prompt)
    return response.text


# Step 4: Main script
def main():
    commits = get_commits_for_current_week(DB_PATH)

    # Format the commits
    commit_summary = format_commits(commits)
    print("Formatted Commits:\n", commit_summary)

    # Get the summary from OpenAI
    summary = summarize_commits_with_openai(commit_summary)
    print("\nWeekly Summary:\n", summary)


if __name__ == "__main__":
    main()
