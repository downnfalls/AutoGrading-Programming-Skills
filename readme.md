## Setup

Install Node.js 20.19+ and Python 3.9+, then run these commands from the project folder:

```bash
npm install
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
```

Place your Google service account credentials in `credentials.json` and share the
target Google Sheet with that service account using Editor access.

## Run

With the virtual environment activated, run both scripts with one command:

```bash
python run.py
```

This runs `node app.js` first to fetch scores and generate `output.json`, then
runs `main.py` with the same Python interpreter to update Google Sheets.
If either step fails, the runner stops and returns a nonzero exit code.

## Test

[Open Google Sheet (Link)](https://docs.google.com/spreadsheets/d/REDACTED)
