# scraper.py

from datetime import datetime, timedelta
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from config import LOCATION_PREFERENCES, CALENDAR_ID, WIDGET_ID, URL

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found in environment variables. Add it to your .env file.")


def build_payload(start_date: str, end_date: str, page: int = 0, after: str = None) -> dict:
    # Builds the payload for the POST request.
    payload = {
        "calendarId": CALENDAR_ID,
        "widgetId": WIDGET_ID,
        "page": page,
        "values[0][Name]": "Keyword",
        "values[0][Value]": "",
        "values[0][Value2]": "",
        "values[0][ValueKind]": "9",
        "values[1][Name]": "Date+Range",
        "values[1][Value]": f"{start_date}T00:00:00.000Z",
        "values[1][Value2]": f"{end_date}T00:00:00.000Z",
        "values[1][ValueKind]": "6",
        "values[2][Name]": "Time+Range",
        "values[2][Value]": "",
        "values[2][Value2]": "",
        "values[2][ValueKind]": "7",
        "values[3][Name]": "Age",
        "values[3][Value]": "0",
        "values[3][Value2]": "1188",
        "values[3][ValueKind]": "0",
        "__RequestVerificationToken": TOKEN
    }
    if after:
        payload["after"] = after
    return payload


def extract_data(num_days: int) -> pd.DataFrame:
    # Extract swim times starting today for num_days days.
    start_dt = datetime.today()
    end_dt = start_dt + timedelta(days=num_days)
    start_date, end_date = start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")

    rows, page, after = [], 0, None
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    while True:
        payload = build_payload(start_date, end_date, page, after)
        response = requests.post(URL, data=payload, headers=headers)
        data = response.json()

        classes = data.get("classes", [])
        if not classes:
            break

        for cls in classes:
            if cls.get("Location") in LOCATION_PREFERENCES:
                rows.append({
                    "Location": cls.get("Location"),
                    "Start Date": cls.get("FormattedStartDate"),
                    "Start Time": cls.get("FormattedStartTime"),
                    "End Date": cls.get("FormattedEndDate"),
                    "End Time": cls.get("FormattedEndTime")
                })

        after = data.get("nextKey")
        if not after:
            break
        page += 1

    return pd.DataFrame(rows)


if __name__ == "__main__":
    swim_times = extract_data(num_days=30)
    swim_times.to_csv("swim_times.csv", index=False)
