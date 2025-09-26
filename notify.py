# notify.py

import os
import requests

TELEGRAM_KEY = os.getenv('TELEGRAM_KEY')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_KEY or not CHAT_ID:
    raise ValueError('Telegram token or chat ID not set in environment variables.')


def send_message(message: str) -> bool:
    # Sends a message to the configured Telegram chat via bot.
    url = f'https://api.telegram.org/bot{TELEGRAM_KEY}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
    }

    try:
        return requests.post(url, data=payload).ok
    except requests.RequestException as e:
        print(f'Failed to send Telegram message: {e}')
        return False
