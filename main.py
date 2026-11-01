import json
import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

required = ("GOOGLE_SHEET_ID", "GOOGLE_PROJECT_ID", "GOOGLE_CLIENT_EMAIL", "GOOGLE_PRIVATE_KEY")
missing = [name for name in required if not os.environ.get(name, "").strip()]
if missing:
    raise SystemExit("Missing environment variables: " + ", ".join(missing))

SHEET_ID = os.environ["GOOGLE_SHEET_ID"]

# ===== Auth =====
creds = Credentials.from_service_account_info(
    {
        "type": "service_account",
        "project_id": os.environ["GOOGLE_PROJECT_ID"],
        "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
        "private_key": os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token",
    },
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)

# ===== read JSON file =====
with open("output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ===== loop all sheet =====
for sheet in sh.worksheets():

    week_list = [x.strip() for x in sheet.row_values(1)]
    roll_list = [x.strip() for x in sheet.col_values(1)]

    roll_to_row = {}
    for i in range(1, len(roll_list)):
        roll_to_row[roll_list[i]] = i + 1

    week_to_col = {}
    for i in range(1, len(week_list)):
        week_to_col[week_list[i]] = i + 1

    updates = []
    for roll, scores in data.items():
        roll = roll.strip()
        if roll not in roll_to_row:
            continue
        r = roll_to_row[roll]

        for week, score in scores.items():
            week = week.strip()
            if week not in week_to_col:
                continue
            c = week_to_col[week]
            updates.append({
                "range": gspread.utils.rowcol_to_a1(r, c),
                "values": [[score]]
            })

    if updates:
        sheet.batch_update(updates)
