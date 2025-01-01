import sqlite3
from datetime import datetime, timedelta
from google import genai
from .setup_db import DB_PATH
from .config import config


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
        SELECT datetime(timestamp, 'unixepoch'), repo_name, commit_message, added_lines
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
    for timestamp, message, repo_name, added_lines in commits:
        repo = repo_name.split("/")[1] if "/" in repo_name else repo_name
        formatted.append(f"- [{timestamp}] {repo}: {message}, add lines: {added_lines}")
    return "\n".join(formatted)


# Step 3: Summarize commits using Gemini
def summarize_commits_with_gemini(commit_summary):
    if not commit_summary:
        return "No commits were made this week."

    # Create Gemini model instance
    api_key = config.get("gemini", "api_key")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    Below is the list of Git commits made this week. Summarize the work done by repo during the week:
    {commit_summary}
    Use Chinese return format markdown as below, percentage is calculated based on the number of addedlines, remove username in repo_name:
    - repo_name: works [percentage]
    - repo_name: works [percentage]
    """

    # Generate response
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=prompt
    )
    return response.text


# Step 4: Main script
def summarize_week_commit():
    commits = get_commits_for_current_week(DB_PATH)

    # Format the commits
    commit_summary = format_commits(commits)
    print("Formatted Commits:\n", commit_summary)

    # Get the summary from OpenAI
    summary = summarize_commits_with_gemini(commit_summary)
    print("\nWeekly Summary:\n", summary)
