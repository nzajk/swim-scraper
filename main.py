# main.py

import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from scraper import cache_data
from notify import send_message
from config import CSV_FILE_NAME

load_dotenv()

TOKEN = os.getenv('TOKEN')
TELEGRAM_KEY = os.getenv('TELEGRAM_KEY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TOKEN:
    raise ValueError('TOKEN not found in .env')
if not TELEGRAM_KEY or not CHAT_ID:
    raise ValueError('Telegram token or chat ID not found in .env')


def main():
    try:
        cache_data(CSV_FILE_NAME)
    except Exception as e:
        print(f"An error occurred: {e}")

    df = pd.read_csv(CSV_FILE_NAME)
    today_df = df[df['Start Date'] == datetime.today().strftime('%Y-%m-%d')]

    if today_df.empty:
        return

    message_lines = [
        f"{row['Start Time']} - {row['End Time']}" 
        for _, row in today_df.iterrows()
    ]
    location = today_df.iloc[0]['Location']
    message = f"🏊 Today's Swim Times at {location}:\n" + "\n".join(message_lines)

    send_message(message)

if __name__ == '__main__':
    main()
