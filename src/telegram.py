import os
import requests

class Telegram:
    def __init__(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN")

        self.base = f"https://api.telegram.org/bot{token}"

    def get_updates(self):
        return requests.get(f"{self.base}/getUpdates", timeout=15).json()

    def send_message(self, chat_id, text):
        return requests.post(
            f"{self.base}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        ).json()

    def send_file(self, chat_id, path, caption=""):
        with open(path, "rb") as f:
            return requests.post(
                f"{self.base}/sendDocument",
                data={"chat_id": chat_id, "caption": caption},
                files={"document": f}
            ).json()
