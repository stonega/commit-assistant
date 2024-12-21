#!/usr/bin/env python3

from google import genai
import subprocess
import os


def get_code_diff():
    """
    Get the code diff of the staged changes.
    """
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--cached"], universal_newlines=True
        ).strip()
        return diff
    except subprocess.CalledProcessError:
        print(
            "Error: Failed to get git diff. Make sure you're in a git repository and have staged changes."
        )
        return None


def generate_commit_message(diff):
    """
    Generate a commit message using Gemini AI based on the code diff.
    """
    if not diff:
        return None

    # Create Gemini model instance
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    As a Git commit message generator, analyze the following code changes and create a clear, 
    concise commit message following these rules:
    1. Start with a type prefix (feat, fix, docs, style, refactor, test, chore)
    2. Keep the first line under 50 characters
    3. Use the imperative mood ("add" not "added")
    4. Focus on the "what" and "why", not the "how"
    5. If needed, add detailed explanation after a blank line

    Here are the code changes:

    {diff}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error generating commit message: {str(e)}")
        return None


def main():
    """
    Main function to generate and apply commit message.
    """
    # Get the code diff
    diff = get_code_diff()
    if not diff:
        print("No staged changes found. Please stage your changes first.")
        return

    # Generate commit message
    commit_message = generate_commit_message(diff)
    if not commit_message:
        print("Failed to generate commit message.")
        return

    print("\nGenerated commit message:")
    print("------------------------")
    print(commit_message)
    print("------------------------")
    # Ask for confirmation
    response = input("\nWould you like to use this commit message? (y/n): ").lower()
    if response == "y":
        try:
            # Write commit message to temporary file
            temp_file = ".git/COMMIT_EDITMSG"
            with open(temp_file, "w") as f:
                f.write(commit_message)

            # Allow user to edit the message
            subprocess.call(["vim", temp_file])

            # Read the possibly modified message
            with open(temp_file, "r") as f:
                final_message = f.read()

            # Commit with the message
            subprocess.run(["git", "commit", "-m", final_message], check=True)
            print("Commit successful!")
        except Exception as e:
            print(f"Error creating commit: {str(e)}")
    else:
        print("Commit cancelled.")


if __name__ == "__main__":
    main()
