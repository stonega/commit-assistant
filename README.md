# Commit Assistant

[![PyPI version](https://badge.fury.io/py/commit-assistant.svg)](https://badge.fury.io/py/commit-assistant)
This project tracks Git commits and README file versions by saving them to an SQLite database using a post-commit hook.

## Features
- Generate commit message with Gemini.
- Save commit metadata (author, timestamp, message, code diff) in SQLite.
- Generate commit summary with Gemini.

## Usage

```bash
## setup 
coas setup
## setup husky hooks, run inside you project directory if husky enabled
coas setup-husky
## generate commit message with Gemini
coas commit
## summary commits for latest week
coas summary
```
