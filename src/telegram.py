import os
import requests

class Telegram:
    def __init__(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            raise ValueError("Missing TELEGRAM_BOT_TOKEN")

        self.base = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id, text):
        requests.post(
            f"{self.base}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )

    def send_file(self, chat_id, file_path, caption=""):
        with open(file_path, "rb") as f:
            requests.post(
                f"{self.base}/sendDocument",
                data={"chat_id": chat_id, "caption": caption},
                files={"document": f}
            )

    def get_updates(self):
        return requests.get(f"{self.base}/getUpdates").json()
