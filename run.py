"""Fetch current scores, then upload them to Google Sheets."""

from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
import subprocess
import shutil
import sys


def requirements_installed(requirements_path):
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        requirement = line.split("#", 1)[0].strip()
        if not requirement:
            continue
        name, separator, expected = requirement.partition("==")
        if not separator:
            return False  # Let pip handle requirements that are not exact pins.
        try:
            if version(name.strip()) != expected.strip():
                return False
        except PackageNotFoundError:
            return False
    return True


def main():
    project_dir = Path(__file__).resolve().parent
    steps = []
    if not requirements_installed(project_dir / "requirements.txt"):
        steps.append(("Installing Python requirements", [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]))
    else:
        print("Python requirements already installed; skipping installation.", flush=True)
    npm = shutil.which("npm") or "npm"
    try:
        js_ready = subprocess.run(
            [npm, "ls", "--omit=dev", "--depth=0"], cwd=project_dir,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
    except FileNotFoundError:
        print("npm not found. Install Node.js and check PATH.", file=sys.stderr)
        return 1
    if not js_ready:
        steps.append(("Installing JavaScript dependencies", [npm, "install"]))
    else:
        print("JavaScript dependencies already installed; skipping installation.", flush=True)
    steps.extend([
        ("Fetching scores (app.js)", ["node", "app.js"]),
        ("Updating Google Sheets (main.py)", [sys.executable, "main.py"]),
    ])

    for description, command in steps:
        print(description, flush=True)
        try:
            subprocess.run(command, cwd=project_dir, check=True)
        except FileNotFoundError:
            print(f"Command not found: {command[0]}. Install it and check PATH.", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as error:
            print(f"{description} failed (exit code {error.returncode}). Stopping.", file=sys.stderr)
            return error.returncode

    print("Scores updated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
