import json
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "REDACTED"

# ===== Auth =====
creds = Credentials.from_service_account_file(
    "credentials.json",
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
