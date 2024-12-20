import sqlite3
from datetime import datetime, timedelta
from openai import OpenAI
import os

DB_PATH = os.getenv("COMMIT_DB_PATH", "./database/commits.db")


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


# Step 3: Summarize commits using OpenAI
def summarize_commits_with_openai(commit_summary):
    if not commit_summary:
        return "No commits were made this week."
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url="https://aihubmix.com"
    )

    prompt = f"""
    Below is the list of Git commits made this week. Summarize the work done during the week in a concise and professional manner:
    
    {commit_summary}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content


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
