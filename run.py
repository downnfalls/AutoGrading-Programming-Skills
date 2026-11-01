"""Fetch current scores, then upload them to Google Sheets."""

from pathlib import Path
import subprocess
import sys


def main():
    project_dir = Path(__file__).resolve().parent
    steps = [
        ("Fetching scores (app.js)", ["node", "app.js"]),
        ("Updating Google Sheets (main.py)", [sys.executable, "main.py"]),
    ]

    for description, command in steps:
        print(description, flush=True)
        try:
            subprocess.run(command, cwd=project_dir, check=True)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}. Install it and check PATH.", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as error:
            print(f"{command[1]} failed (exit code {error.returncode}). Stopping.", file=sys.stderr)
            return error.returncode

    print("Scores updated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
