# scraper.py

from datetime import datetime, timedelta
import os
import requests
import re
import pandas as pd
from config import LOCATION_PREFERENCES, CALENDAR_ID, WIDGET_ID, URL, NUM_DAYS

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError('TOKEN not found in environment variables. Add it to your .env file.')


def build_payload(start_date: str, end_date: str, page: int = 0, after: str = None) -> dict:
    # Builds the payload for the POST request.
    payload = {
        'calendarId': CALENDAR_ID,
        'widgetId': WIDGET_ID,
        'page': page,
        'values[0][Name]': 'Keyword',
        'values[0][Value]': '',
        'values[0][Value2]': '',
        'values[0][ValueKind]': '9',
        'values[1][Name]': 'Date+Range',
        'values[1][Value]': f'{start_date}T00:00:00.000Z',
        'values[1][Value2]': f'{end_date}T00:00:00.000Z',
        'values[1][ValueKind]': '6',
        'values[2][Name]': 'Time+Range',
        'values[2][Value]': '',
        'values[2][Value2]': '',
        'values[2][ValueKind]': '7',
        'values[3][Name]': 'Age',
        'values[3][Value]': '0',
        'values[3][Value2]': '1188',
        'values[3][ValueKind]': '0',
        '__RequestVerificationToken': TOKEN
    }
    if after:
        payload['after'] = after
    return payload


def remove_ordinal_suffix(date_str: str) -> str:
    return re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str)


def extract_data(num_days: int) -> pd.DataFrame:
    start_dt = datetime.today()
    end_dt = start_dt + timedelta(days=num_days)
    start_date, end_date = start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d')

    rows, page, after = [], 0, None
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    while True:
        payload = build_payload(start_date, end_date, page, after)
        response = requests.post(URL, data=payload, headers=headers)
        data = response.json()

        classes = data.get('classes', [])
        if not classes:
            break

        for cls in classes:
            if cls.get('Location') in LOCATION_PREFERENCES:
                start_str = remove_ordinal_suffix(cls.get('FormattedStartDate')) + ' ' + cls.get('FormattedStartTime')
                start_dt_obj = datetime.strptime(start_str, '%a, %b %d, %Y %I:%M %p')

                end_date_str = remove_ordinal_suffix(cls.get('FormattedEndDate'))
                end_str = f'{end_date_str} {start_dt_obj.year} {cls.get("FormattedEndTime")}'
                end_dt_obj = datetime.strptime(end_str, '%b %d %Y %I:%M %p')
                
                rows.append({
                    'Location': cls.get('Location'),
                    'Start Date': start_dt_obj.strftime('%Y-%m-%d'),
                    'Start Time': start_dt_obj.strftime('%H:%M'),
                    'End Date': end_dt_obj.strftime('%Y-%m-%d'),
                    'End Time': end_dt_obj.strftime('%H:%M')
                })

        after = data.get('nextKey')
        if not after:
            break
        page += 1

    return pd.DataFrame(rows)


def cache_data(file_name):
    swim_times = extract_data(num_days=NUM_DAYS)

    if os.path.exists(file_name):
        existing_df = pd.read_csv(file_name)
        new_rows = pd.merge(
            swim_times, existing_df,
            how='outer', indicator=True
        ).query('_merge == "left_only"').drop(columns=['_merge'])
        if not new_rows.empty:
            updated_df = pd.concat([existing_df, new_rows], ignore_index=True)
            updated_df.to_csv(file_name, index=False)
    else:
        swim_times.to_csv(file_name, index=False)
