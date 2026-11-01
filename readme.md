## Setup

Install Node.js 20.19+ (including npm) and Python 3.10+, then run these commands from the project folder:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

```

Copy `.env.example` to `.env`:

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

```bash
# macOS / Linux
cp .env.example .env
```

Fill in the Google Sheet ID, Google service account project ID, email, private key,
and both VJudge group IDs in `.env`. Use a newly issued private key and write line
breaks as `\n` inside the quoted `GOOGLE_PRIVATE_KEY` value. Share your Google Sheet
with the service account email using Editor access. Environment variables already
set in the shell take precedence over `.env`.

Never commit `.env` or service account key files. `.gitignore` excludes these files,
virtual environments, installed packages, and generated score files.

## Run

With the virtual environment activated, run both scripts with one command:

```bash
python run.py
```

The runner checks Python packages against `requirements.txt` and JavaScript
packages against `package.json`. It runs `python -m pip install -r requirements.txt`
or `npm install` only for a dependency set that is missing or has incompatible
versions. Internet access is required when installation is needed.

It then runs `node app.js` first to fetch scores and generate `output.json`, then
runs `main.py` with the same Python interpreter to update Google Sheets.
If either step fails, the runner stops and returns a nonzero exit code.

Open the Google Sheet configured by `GOOGLE_SHEET_ID` to check the uploaded scores.

Previously exposed keys must be revoked in Google Cloud IAM and replaced. Removing
them from Git history does not invalidate copies of an old key. After the history
cleanup, collaborators should clone the repository again instead of merging an old clone.
