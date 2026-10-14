import os
import sys
import requests


def send(message: str) -> None:
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    try:
        print(message)
    except UnicodeEncodeError:  # cp1252 Windows consoles can't print emoji
        sys.stdout.buffer.write(message.encode("utf-8", "replace") + b"\n")
        sys.stdout.buffer.flush()
    if not token or not chat:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": message},
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"(telegram failed: {e})")
