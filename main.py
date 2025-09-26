from datetime import date
import requests
import pandas as pd

date = date.today().isoformat()

payload = {
    "calendarId": "a63742fd-71f9-471b-a2b7-0958d5629622",
    "widgetId": "4cc6bb5d-4261-4f91-9533-62eebea54c8a",
    "occurrenceDate": date
}
headers = {
    "Content-Type": "application/json"
}
location_preferences = {'Dalewood Recreation Centre'}

# todo: extract more dates at a time, right now it only pulls the next 3 days.
def extract_data(payload, headers, location_preferences):
    url = "https://cityofhamilton.perfectmind.com/39117/Clients/BookMe4BookingPagesV2/ClassesV2"
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    rows = []
    for cls in data.get('classes', []):
        row = {
            "Location": cls.get("Location"),
            "Start Date": cls.get("FormattedStartDate"),
            "Start Time": cls.get("FormattedStartTime"),
            "End Date": cls.get("FormattedEndDate"),
            "End Time": cls.get("FormattedEndTime")
        }

        if cls.get('Location') in location_preferences:
            rows.append(row)
    
    df = pd.DataFrame(rows)

    return df

# todo: send push notifications via telegram.
def notify():
    pass

swim_times = extract_data(payload, headers, location_preferences)
print(swim_times)